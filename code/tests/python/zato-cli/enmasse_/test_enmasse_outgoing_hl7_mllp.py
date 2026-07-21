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

_Outgoing_HL7_MLLP_Template = """

outgoing_hl7_mllp:

  - name: enmasse.hl7.mllp.out.1.{test_suffix}
    address: 127.0.0.1:30901

  - name: enmasse.hl7.mllp.out.2.{test_suffix}
    address: 127.0.0.1:30902
    recv_timeout: 500
    max_msg_size: 1000000
    should_log_messages: true

  - name: enmasse.hl7.mllp.out.3.{test_suffix}
    address: 127.0.0.1:30903
    start_seq: '0b'
    end_seq: '1c 0d'
    logging_level: DEBUG
    max_retries: 3
    backoff_base_seconds: 2
    tls_ca_path: /path/to/ca.pem
    tls_cert_path: /path/to/client.pem
    tls_key_path: /path/to/client.key

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingHL7MLLPLive(BaseEnmasseTestCase):
    """ Live CLI tests for outgoing HL7 MLLP import, export, and reimport against a real server.
    """

    def _cleanup(self, test_suffix:'str') -> 'None':
        from zato.cli.enmasse.client import cleanup_enmasse
        from zato.common.defaults import default_server_base_dir
        cleanup_enmasse(default_server_base_dir)

# ################################################################################################################################

    def test_outgoing_hl7_mllp_import_export_reimport(self) -> 'None':
        """ Full cycle: import outgoing HL7 MLLP connections, export them, verify the export, then reimport to confirm idempotency.
        """

        # sh
        from sh import ErrorReturnCode

        os.environ['Zato_Needs_Config_Reload'] = 'False'

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        import_file_name = 'zato-enmasse-hl7-out-import-' + test_suffix + '.yaml'
        export_file_name = 'zato-enmasse-hl7-out-export-' + test_suffix + '.yaml'

        import_path = os.path.join(tmp_dir, import_file_name)
        export_path = os.path.join(tmp_dir, export_file_name)

        # Prepare the import file from the template ..
        data = _Outgoing_HL7_MLLP_Template.format(test_suffix=test_suffix)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:

            # .. import the outgoing HL7 MLLP connections ..
            _ = self.invoke_enmasse(import_path)

            # .. export them back out ..
            _ = self.invoke_enmasse(export_path, is_import=False, is_export=True, include_type='outgoing_hl7_mllp')

            # .. read the exported file ..
            with open(export_path, 'r') as f:
                export_data = f.read()

            exported_dict = yaml.safe_load(export_data)

            # .. confirm the exported YAML has the outgoing_hl7_mllp key ..
            self.assertIn('outgoing_hl7_mllp', exported_dict, 'outgoing_hl7_mllp key missing from export')

            exported_connections = exported_dict['outgoing_hl7_mllp']

            # .. filter to our test connections ..
            test_connections = []
            for connection in exported_connections:
                if test_suffix in connection['name']:
                    test_connections.append(connection)

            test_connection_count = len(test_connections)
            self.assertEqual(test_connection_count, 3, f'Expected 3 outgoing HL7 MLLP connections, found {test_connection_count}')

            # .. verify key fields survived the round trip ..
            connections_by_name = {}
            for connection in test_connections:
                connections_by_name[connection['name']] = connection

            connection_1_name = f'enmasse.hl7.mllp.out.1.{test_suffix}'
            connection_2_name = f'enmasse.hl7.mllp.out.2.{test_suffix}'
            connection_3_name = f'enmasse.hl7.mllp.out.3.{test_suffix}'

            self.assertEqual(connections_by_name[connection_1_name]['address'], '127.0.0.1:30901')

            self.assertEqual(connections_by_name[connection_2_name]['address'], '127.0.0.1:30902')
            self.assertEqual(connections_by_name[connection_2_name]['recv_timeout'], 500)
            self.assertEqual(connections_by_name[connection_2_name]['max_msg_size'], 1000000)
            self.assertEqual(connections_by_name[connection_2_name]['should_log_messages'], True)

            self.assertEqual(connections_by_name[connection_3_name]['logging_level'], 'DEBUG')
            self.assertEqual(connections_by_name[connection_3_name]['max_retries'], 3)
            self.assertEqual(connections_by_name[connection_3_name]['backoff_base_seconds'], 2)
            self.assertEqual(connections_by_name[connection_3_name]['tls_ca_path'], '/path/to/ca.pem')
            self.assertEqual(connections_by_name[connection_3_name]['tls_cert_path'], '/path/to/client.pem')
            self.assertEqual(connections_by_name[connection_3_name]['tls_key_path'], '/path/to/client.key')

            # .. now reimport the exported file to confirm idempotency ..
            _ = self.invoke_enmasse(export_path)

            # .. and export again to make sure nothing drifted.
            reimport_export_file_name = 'zato-enmasse-hl7-out-reimport-export-' + test_suffix + '.yaml'
            reimport_export_path = os.path.join(tmp_dir, reimport_export_file_name)

            _ = self.invoke_enmasse(reimport_export_path, is_import=False, is_export=True, include_type='outgoing_hl7_mllp')

            with open(reimport_export_path, 'r') as f:
                reimport_data = f.read()

            reimport_dict = yaml.safe_load(reimport_data)

            reimport_connections = []
            for connection in reimport_dict['outgoing_hl7_mllp']:
                if test_suffix in connection['name']:
                    reimport_connections.append(connection)

            reimport_count = len(reimport_connections)
            self.assertEqual(reimport_count, 3, f'Reimport produced {reimport_count} connections instead of 3')

            if os.path.exists(reimport_export_path):
                os.remove(reimport_export_path)

        except ErrorReturnCode as error:
            stdout = error.stdout.decode('utf8')
            stderr = error.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception during outgoing HL7 MLLP import-export-reimport; stdout -> {stdout}')

        finally:
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(export_path):
                os.remove(export_path)

            self._cleanup(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
