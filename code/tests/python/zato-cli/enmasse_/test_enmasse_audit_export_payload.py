# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from unittest import main

# PyYAML
import yaml

# Zato
from zato.common.test import rand_string, rand_unicode
from zato.common.test.enmasse_.base import BaseEnmasseTestCase
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The key under test and the object types that carry it - every type whose events hold payloads
Flag = 'is_audit_export_payload_active'

Object_Types = (
    'channel_rest',
    'channel_soap',
    'outgoing_rest',
    'outgoing_soap',
    'email_imap',
    'email_smtp',
    'pubsub_topic',
    'outgoing_as2',
    'channel_as4',
    'outgoing_as4',
    'sql',
    'channel_kafka',
    'outgoing_kafka',
    'outgoing_fhir',
    'channel_mllp',
    'outgoing_mllp',
)

# Each type has one object with the flag on and one that does not mention it
_Template = """

channel_rest:

  - name: enmasse.payload.channel.rest.on.{suffix}
    service: demo.ping
    url_path: /enmasse/payload/rest/on/{suffix}
    is_audit_export_payload_active: true

  - name: enmasse.payload.channel.rest.off.{suffix}
    service: demo.ping
    url_path: /enmasse/payload/rest/off/{suffix}

channel_soap:

  - name: enmasse.payload.channel.soap.on.{suffix}
    service: demo.ping
    url_path: /enmasse/payload/soap/on/{suffix}
    soap_action: urn:enmasse.payload.on
    is_audit_export_payload_active: true

  - name: enmasse.payload.channel.soap.off.{suffix}
    service: demo.ping
    url_path: /enmasse/payload/soap/off/{suffix}
    soap_action: urn:enmasse.payload.off

outgoing_rest:

  - name: enmasse.payload.outgoing.rest.on.{suffix}
    host: https://crm.example.com
    url_path: /api/v2/customers
    is_audit_export_payload_active: true

  - name: enmasse.payload.outgoing.rest.off.{suffix}
    host: https://crm.example.com
    url_path: /api/v2/orders

outgoing_soap:

  - name: enmasse.payload.outgoing.soap.on.{suffix}
    host: https://crm.example.com
    url_path: /soap/customers
    soap_action: urn:GetCustomer
    is_audit_export_payload_active: true

  - name: enmasse.payload.outgoing.soap.off.{suffix}
    host: https://crm.example.com
    url_path: /soap/orders
    soap_action: urn:GetOrder

email_imap:

  - name: enmasse.payload.imap.on.{suffix}
    host: imap.example.com
    port: 993
    username: enmasse.on@example.com
    is_audit_export_payload_active: true

  - name: enmasse.payload.imap.off.{suffix}
    host: imap.example.com
    port: 993
    username: enmasse.off@example.com

email_smtp:

  - name: enmasse.payload.smtp.on.{suffix}
    host: smtp.example.com
    port: 587
    is_audit_export_payload_active: true

  - name: enmasse.payload.smtp.off.{suffix}
    host: smtp.example.com
    port: 587

pubsub_topic:

  - name: enmasse.payload.topic.on.{suffix}
    is_audit_export_payload_active: true

  - name: enmasse.payload.topic.off.{suffix}

outgoing_as2:

  - name: enmasse.payload.as2.on.{suffix}
    as2_from: ENMASSE-ON
    as2_to: PARTNER-ON
    endpoint_url: https://as2.example.com/on
    is_audit_export_payload_active: true

  - name: enmasse.payload.as2.off.{suffix}
    as2_from: ENMASSE-OFF
    as2_to: PARTNER-OFF
    endpoint_url: https://as2.example.com/off

channel_as4:

  - name: enmasse.payload.channel.as4.on.{suffix}
    url_path: /enmasse/payload/as4/on/{suffix}
    is_audit_export_payload_active: true

  - name: enmasse.payload.channel.as4.off.{suffix}
    url_path: /enmasse/payload/as4/off/{suffix}

outgoing_as4:

  - name: enmasse.payload.outgoing.as4.on.{suffix}
    host: https://as4.example.com
    url_path: /msh/on
    is_audit_export_payload_active: true

  - name: enmasse.payload.outgoing.as4.off.{suffix}
    host: https://as4.example.com
    url_path: /msh/off

sql:

  - name: enmasse.payload.sql.on.{suffix}
    type: postgresql
    host: db.example.com
    port: 5432
    db_name: enmasse_on
    username: enmasse_on
    is_audit_export_payload_active: true

  - name: enmasse.payload.sql.off.{suffix}
    type: postgresql
    host: db.example.com
    port: 5432
    db_name: enmasse_off
    username: enmasse_off

channel_kafka:

  - name: enmasse.payload.channel.kafka.on.{suffix}
    address: kafka.example.com:9092
    is_audit_export_payload_active: true

  - name: enmasse.payload.channel.kafka.off.{suffix}
    address: kafka.example.com:9092

outgoing_kafka:

  - name: enmasse.payload.outgoing.kafka.on.{suffix}
    address: kafka.example.com:9092
    is_audit_export_payload_active: true

  - name: enmasse.payload.outgoing.kafka.off.{suffix}
    address: kafka.example.com:9092

outgoing_fhir:

  - name: enmasse.payload.fhir.on.{suffix}
    address: http://127.0.0.1:31301/fhir/r4
    is_audit_export_payload_active: true

  - name: enmasse.payload.fhir.off.{suffix}
    address: http://127.0.0.1:31302/fhir/r4

channel_mllp:

  - name: enmasse.payload.channel.mllp.on.{suffix}
    service: demo.ping
    is_audit_export_payload_active: true

  - name: enmasse.payload.channel.mllp.off.{suffix}
    service: demo.ping

outgoing_mllp:

  - name: enmasse.payload.outgoing.mllp.on.{suffix}
    address: 10.20.30.40:2575
    is_audit_export_payload_active: true

  - name: enmasse.payload.outgoing.mllp.off.{suffix}
    address: 10.20.30.40:2576

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseAuditExportPayloadLive(BaseEnmasseTestCase):
    """ Live CLI tests for the audit export payload flag - imported for every object type that carries it,
    exported only when it is on, and absent from the export of an object that never set it.
    """

    def _cleanup(self) -> 'None':
        from zato.cli.enmasse.client import cleanup_enmasse
        from zato.common.defaults import default_server_base_dir
        cleanup_enmasse(default_server_base_dir)

# ################################################################################################################################

    def _export(self, export_path:'str', suffix:'str') -> 'dict':
        """ Exports every object type under test and answers with the objects this test created,
        keyed first by type and then by name.
        """
        _ = self.invoke_enmasse(export_path, is_import=False, is_export=True, include_type=','.join(Object_Types))

        with open(export_path, 'r') as f:
            export_data = f.read()

        exported_dict = yaml.safe_load(export_data)

        out = {}

        for object_type in Object_Types:
            self.assertIn(object_type, exported_dict, f'{object_type} key missing from export')

            by_name = {}
            for item in exported_dict[object_type]:
                if suffix in item['name']:
                    by_name[item['name']] = item

            out[object_type] = by_name

        return out

# ################################################################################################################################

    def _assert_flag_round_trip(self, exported:'dict', suffix:'str') -> 'None':
        """ Each type has exactly one object with the flag exported as True and one with no flag at all.
        """
        for object_type in Object_Types:
            by_name = exported[object_type]

            count = len(by_name)
            self.assertEqual(count, 2, f'Expected 2 {object_type} objects, found {count}: {sorted(by_name)}')

            with_flag = []
            without_flag = []

            for name, item in by_name.items():
                if Flag in item:
                    self.assertIs(item[Flag], True, f'{object_type} {name} exported {Flag} as {item[Flag]!r}')
                    with_flag.append(name)
                else:
                    without_flag.append(name)

            self.assertEqual(len(with_flag), 1, f'{object_type}: {Flag} should be on exactly one object, found {with_flag}')
            self.assertEqual(len(without_flag), 1, f'{object_type}: {Flag} should be absent from exactly one object, found {without_flag}')

            self.assertIn('.on.', with_flag[0], f'{object_type}: the flag landed on the wrong object, {with_flag[0]}')
            self.assertIn('.off.', without_flag[0], f'{object_type}: the flag is missing from the wrong object, {without_flag[0]}')

# ################################################################################################################################

    def test_payload_flag_import_export_reimport(self) -> 'None':
        """ Full cycle: import one object of each type with the flag on and one without, export them,
        check that the flag leaves only with the one that has it, then reimport the export and check nothing drifted.
        """

        # sh
        from sh import ErrorReturnCode

        os.environ['Zato_Needs_Config_Reload'] = 'False'

        tmp_dir = gettempdir()
        suffix = rand_unicode() + '.' + rand_string()

        import_path = os.path.join(tmp_dir, 'zato-enmasse-payload-import-' + suffix + '.yaml')
        export_path = os.path.join(tmp_dir, 'zato-enmasse-payload-export-' + suffix + '.yaml')
        reimport_export_path = os.path.join(tmp_dir, 'zato-enmasse-payload-reimport-export-' + suffix + '.yaml')

        data = _Template.format(suffix=suffix)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:

            # .. import one object of each type with the flag on and one without ..
            _ = self.invoke_enmasse(import_path)

            # .. the export carries the flag only where it is on ..
            exported = self._export(export_path, suffix)
            self._assert_flag_round_trip(exported, suffix)

            # .. reimporting the export updates rather than duplicates ..
            _ = self.invoke_enmasse(export_path)

            # .. and a second export shows the same picture.
            reimported = self._export(reimport_export_path, suffix)
            self._assert_flag_round_trip(reimported, suffix)

        except ErrorReturnCode as error:
            stdout = error.stdout.decode('utf8')
            stderr = error.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception during the payload flag import-export-reimport; stdout -> {stdout}')

        finally:
            for path in [import_path, export_path, reimport_export_path]:
                if os.path.exists(path):
                    os.remove(path)

            self._cleanup()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
