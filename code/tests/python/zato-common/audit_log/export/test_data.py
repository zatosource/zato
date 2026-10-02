# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import dumps
from unittest import TestCase

# Zato
from zato.common.audit_log.common import AuditEvent, AuditSource
from zato.common.audit_log.export.config import get_all_sources
from zato.common.audit_log.export.data import build_data_attributes, build_payload_attributes, flatten, get_sources_with_data, \
    get_sources_without_data, has_data_export, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict

# ################################################################################################################################
# ################################################################################################################################

def _data(name:'str') -> 'str':
    out = f'{ModuleCtx.Data_Prefix}.{name}'
    return out

# ################################################################################################################################
# ################################################################################################################################

class TestFlatten(TestCase):

    def test_nested_objects_join_with_a_dot(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'auth': {'identity': 'maria', 'nested': {'deep': 1}}, 'top': 'value'}, out)

        self.assertEqual(out, {
            'root.auth.identity': 'maria',
            'root.auth.nested.deep': 1,
            'root.top': 'value',
        })

# ################################################################################################################################

    def test_scalars_keep_their_types(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'text': 'a', 'number': 2, 'ratio': 2.5, 'flag': False}, out)

        self.assertEqual(out['root.text'], 'a')
        self.assertIs(type(out['root.number']), int)
        self.assertIs(type(out['root.ratio']), float)
        self.assertIs(out['root.flag'], False)

# ################################################################################################################################

    def test_list_of_one_scalar_type_stays_an_array(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'scopes': ['a', 'b'], 'counts': [1, 2, 3]}, out)

        self.assertEqual(out['root.scopes'], ('a', 'b'))
        self.assertEqual(out['root.counts'], (1, 2, 3))

# ################################################################################################################################

    def test_list_of_mixed_scalars_becomes_strings(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'mixed': ['a', 1, True]}, out)

        self.assertEqual(out['root.mixed'], ('a', '1', 'True'))

# ################################################################################################################################

    def test_list_holding_objects_is_serialized(self) -> 'None':

        items = [{'id': 1}, {'id': 2}]

        out:'stranydict' = {}
        flatten('root', {'rows': items, 'lists': [[1], [2]]}, out)

        self.assertEqual(out['root.rows'], dumps(items))
        self.assertEqual(out['root.lists'], dumps([[1], [2]]))

# ################################################################################################################################

    def test_empty_list(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'claims_matched': []}, out)

        self.assertEqual(out['root.claims_matched'], ())

# ################################################################################################################################

    def test_nulls_and_empty_strings_are_left_out(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'present': 'yes', 'absent': None, 'empty': '', 'nested': {'absent': None, 'empty': ''}}, out)

        self.assertEqual(out, {'root.present': 'yes'})

# ################################################################################################################################

    def test_strings_are_capped(self) -> 'None':

        long_value = 'x' * (ModuleCtx.Max_Value_Length + 100)

        out:'stranydict' = {}
        flatten('root', {'long': long_value, 'short': 'abc'}, out)

        self.assertEqual(len(out['root.long']), ModuleCtx.Max_Value_Length)
        self.assertEqual(out['root.long'], 'x' * ModuleCtx.Max_Value_Length)
        self.assertEqual(out['root.short'], 'abc')

        self.assertEqual(ModuleCtx.Max_Value_Length, 4096)

# ################################################################################################################################

    def test_serialized_list_is_capped(self) -> 'None':

        items = []
        for index in range(2000):
            items.append({'id': index, 'name': 'customer-name-' + str(index)})

        out:'stranydict' = {}
        flatten('root', {'rows': items}, out)

        self.assertEqual(len(out['root.rows']), ModuleCtx.Max_Value_Length)

# ################################################################################################################################

    def test_unknown_type_travels_as_text(self) -> 'None':

        out:'stranydict' = {}
        flatten('root', {'other': {1, 2}}, out)

        self.assertIsInstance(out['root.other'], str)

# ################################################################################################################################
# ################################################################################################################################

class TestAllowList(TestCase):

    def test_mcp_sends_every_key(self) -> 'None':

        data = dumps({'remote_address': '10.0.0.1', 'method': 'tools/call', 'auth': {'identity': 'maria'}})

        out:'stranydict' = {}
        build_data_attributes(AuditSource.MCP, AuditEvent.MCP_Tools_Call, data, out)

        self.assertEqual(out, {
            _data('remote_address'): '10.0.0.1',
            _data('method'): 'tools/call',
            _data('auth.identity'): 'maria',
        })

# ################################################################################################################################

    def test_config_and_file_outgoing_send_every_key(self) -> 'None':

        for source in (AuditSource.Config, AuditSource.File_Outgoing):

            out:'stranydict' = {}
            build_data_attributes(source, AuditEvent.Request_Sent, dumps({'a': 1, 'b': {'c': 2}}), out)

            self.assertEqual(out, {_data('a'): 1, _data('b.c'): 2}, source)

# ################################################################################################################################

    def test_sql_outgoing_sends_statement_row_count_and_error(self) -> 'None':

        data = dumps({'statement': 'select 1', 'params': {'id': 1}, 'rows': [{'x': 1}], 'row_count': 1, 'error': ''})

        out:'stranydict' = {}
        build_data_attributes(AuditSource.SQL_Outgoing, AuditEvent.Request_Sent, data, out)

        # An empty error is an empty string, which is left out like any other
        self.assertEqual(out, {
            _data('statement'): 'select 1',
            _data('row_count'): 1,
        })

# ################################################################################################################################

    def test_fhir_sends_resource_type_method_and_path(self) -> 'None':

        data = dumps({'payload': '{}', 'method': 'get', 'path': '/Patient/1', 'params': {}, 'resource_type': 'Patient'})

        out:'stranydict' = {}
        build_data_attributes(AuditSource.FHIR, AuditEvent.Request_Sent, data, out)

        self.assertEqual(out, {
            _data('resource_type'): 'Patient',
            _data('method'): 'get',
            _data('path'): '/Patient/1',
        })

# ################################################################################################################################

    def test_imap_sends_sender_and_recipients(self) -> 'None':

        data = dumps({'subject': 'Report', 'sent_from': 'a@example.com', 'sent_to': 'b@example.com', 'body': 'text'})

        out:'stranydict' = {}
        build_data_attributes(AuditSource.Email_IMAP, AuditEvent.Message_Received, data, out)

        self.assertEqual(out, {
            _data('sent_from'): 'a@example.com',
            _data('sent_to'): 'b@example.com',
        })

# ################################################################################################################################

    def test_as2_sends_mic_and_disposition(self) -> 'None':

        data = dumps({'mic': 'abc=', 'disposition': 'processed', 'payload': 'EDI'})

        out:'stranydict' = {}
        build_data_attributes(AuditSource.AS2, AuditEvent.MDN_Received, data, out)

        self.assertEqual(out, {
            _data('mic'): 'abc=',
            _data('disposition'): 'processed',
        })

# ################################################################################################################################

    def test_alert_raised_of_any_source(self) -> 'None':

        data = dumps({'kind': 'latency', 'message': 'slow', 'rule': 'r1', 'count': 2, 'secret': 'no'})

        for source in (AuditSource.REST_Channel, AuditSource.PubSub, AuditSource.MLLP_Outgoing):

            self.assertTrue(has_data_export(source, AuditEvent.Alert_Raised), source)
            self.assertFalse(has_data_export(source, AuditEvent.Request_Received), source)

            out:'stranydict' = {}
            build_data_attributes(source, AuditEvent.Alert_Raised, data, out)

            self.assertEqual(out, {
                _data('kind'): 'latency',
                _data('message'): 'slow',
                _data('rule'): 'r1',
                _data('count'): 2,
            }, source)

# ################################################################################################################################

    def test_sources_without_data_send_nothing(self) -> 'None':

        for source in get_sources_without_data():
            self.assertFalse(has_data_export(source, AuditEvent.Request_Received), source)

# ################################################################################################################################

    def test_missing_keys_are_skipped(self) -> 'None':

        out:'stranydict' = {}
        build_data_attributes(AuditSource.SQL_Outgoing, AuditEvent.Request_Sent, dumps({'statement': 'select 1'}), out)

        self.assertEqual(out, {_data('statement'): 'select 1'})

# ################################################################################################################################

    def test_empty_non_json_and_non_object_documents(self) -> 'None':

        for data in ('', 'not json', '[1, 2]', '"text"', '42'):

            out:'stranydict' = {}
            build_data_attributes(AuditSource.MCP, AuditEvent.MCP_Tools_Call, data, out)

            self.assertEqual(out, {}, data)

# ################################################################################################################################
# ################################################################################################################################

class TestCoverage(TestCase):

    def test_every_source_has_made_its_decision(self) -> 'None':

        all_sources = get_all_sources()
        with_data = get_sources_with_data()
        without_data = get_sources_without_data()

        self.assertEqual(with_data & without_data, set())
        self.assertEqual(with_data | without_data, all_sources)

# ################################################################################################################################

    def test_all_sources_are_the_audit_source_values(self) -> 'None':

        expected = set()
        for name, value in vars(AuditSource).items():
            if name.startswith('_'):
                continue
            if isinstance(value, str):
                expected.add(value)

        self.assertEqual(get_all_sources(), expected)
        self.assertIn(AuditSource.MCP, expected)
        self.assertIn(AuditSource.REST_Channel, expected)

# ################################################################################################################################
# ################################################################################################################################

class TestPayload(TestCase):

    def test_data_and_bodies_under_the_payload_prefix(self) -> 'None':

        out:'stranydict' = {}
        build_payload_attributes('{"a": 1}', {'request': 'req', 'response': 'resp'}, 1024, out)

        self.assertEqual(out, {
            f'{ModuleCtx.Payload_Prefix}.data': '{"a": 1}',
            f'{ModuleCtx.Payload_Prefix}.request': 'req',
            f'{ModuleCtx.Payload_Prefix}.response': 'resp',
        })

# ################################################################################################################################

    def test_empty_data_is_left_out(self) -> 'None':

        out:'stranydict' = {}
        build_payload_attributes('', {}, 1024, out)

        self.assertEqual(out, {})

# ################################################################################################################################

    def test_cap_and_marker(self) -> 'None':

        out:'stranydict' = {}
        build_payload_attributes('0123456789', {'request': 'abc'}, 4, out)

        self.assertEqual(out[f'{ModuleCtx.Payload_Prefix}.data'], '0123')
        self.assertEqual(out[f'{ModuleCtx.Payload_Prefix}.request'], 'abc')
        self.assertIs(out[ModuleCtx.Payload_Truncated], True)

        out = {}
        build_payload_attributes('0123', {'request': 'abcd'}, 4, out)

        self.assertNotIn(ModuleCtx.Payload_Truncated, out)

# ################################################################################################################################
# ################################################################################################################################
