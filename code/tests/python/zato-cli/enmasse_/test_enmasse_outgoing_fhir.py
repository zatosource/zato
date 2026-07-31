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

_Outgoing_FHIR_Template = """

security:

  - name: enmasse.fhir.sec.{test_suffix}
    type: basic_auth
    username: enmasse.fhir.{test_suffix}
    password: Zato_Enmasse_Env.FHIRRoundTrip

outgoing_fhir:

  - name: enmasse.fhir.out.1.{test_suffix}
    address: http://127.0.0.1:31201/fhir/r4

  - name: enmasse.fhir.out.2.{test_suffix}
    address: http://127.0.0.1:31202/fhir/r4
    pool_size: 5
    is_audit_log_active: true

  - name: enmasse.fhir.out.3.{test_suffix}
    address: http://127.0.0.1:31203/fhir/r4
    security: enmasse.fhir.sec.{test_suffix}

"""

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseOutgoingFHIRLive(BaseEnmasseTestCase):
    """ Live CLI tests for outgoing HL7 FHIR import, export, and reimport against a real server.
    """

    def _cleanup(self, test_suffix:'str') -> 'None':
        from zato.cli.enmasse.client import cleanup_enmasse
        from zato.common.defaults import default_server_base_dir
        cleanup_enmasse(default_server_base_dir)

# ################################################################################################################################

    def _export_connections(self, export_path:'str', test_suffix:'str') -> 'dict':
        """ Exports the outgoing FHIR connections and answers with the ones this test created,
        keyed by the name each of them goes by.
        """
        _ = self.invoke_enmasse(export_path, is_import=False, is_export=True, include_type='outgoing_fhir')

        with open(export_path, 'r') as f:
            export_data = f.read()

        exported_dict = yaml.safe_load(export_data)

        self.assertIn('outgoing_fhir', exported_dict, 'outgoing_fhir key missing from export')

        out = {}

        for connection in exported_dict['outgoing_fhir']:
            if test_suffix in connection['name']:
                out[connection['name']] = connection

        return out

# ################################################################################################################################

    def test_outgoing_fhir_import_export_reimport(self) -> 'None':
        """ Full cycle: import outgoing HL7 FHIR connections, export them, verify the export,
        then reimport to confirm the connections are the same at the end.
        """

        # sh
        from sh import ErrorReturnCode

        os.environ['Zato_Needs_Config_Reload'] = 'False'

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        import_file_name = 'zato-enmasse-fhir-out-import-' + test_suffix + '.yaml'
        export_file_name = 'zato-enmasse-fhir-out-export-' + test_suffix + '.yaml'

        import_path = os.path.join(tmp_dir, import_file_name)
        export_path = os.path.join(tmp_dir, export_file_name)

        reimport_export_file_name = 'zato-enmasse-fhir-out-reimport-export-' + test_suffix + '.yaml'
        reimport_export_path = os.path.join(tmp_dir, reimport_export_file_name)

        # Prepare the import file from the template ..
        data = _Outgoing_FHIR_Template.format(test_suffix=test_suffix)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:

            # .. import the outgoing FHIR connections ..
            _ = self.invoke_enmasse(import_path)

            # .. export them back out ..
            exported = self._export_connections(export_path, test_suffix)

            exported_count = len(exported)
            self.assertEqual(exported_count, 3, f'Expected 3 outgoing FHIR connections, found {exported_count}')

            connection_1_name = f'enmasse.fhir.out.1.{test_suffix}'
            connection_2_name = f'enmasse.fhir.out.2.{test_suffix}'
            connection_3_name = f'enmasse.fhir.out.3.{test_suffix}'

            # .. what was declared is what came back ..
            self.assertEqual(exported[connection_1_name]['address'], 'http://127.0.0.1:31201/fhir/r4')

            self.assertEqual(exported[connection_2_name]['address'], 'http://127.0.0.1:31202/fhir/r4')
            self.assertEqual(exported[connection_2_name]['pool_size'], 5)
            self.assertEqual(exported[connection_2_name]['is_audit_log_active'], True)

            self.assertEqual(exported[connection_3_name]['security'], f'enmasse.fhir.sec.{test_suffix}')

            # .. now reimport the exported file, which must update rather than duplicate ..
            _ = self.invoke_enmasse(export_path)

            # .. and export again to make sure nothing drifted.
            reimported = self._export_connections(reimport_export_path, test_suffix)

            reimport_count = len(reimported)
            self.assertEqual(reimport_count, 3, f'Reimport produced {reimport_count} connections instead of 3')

            self.assertEqual(reimported[connection_2_name]['pool_size'], 5)
            self.assertEqual(reimported[connection_3_name]['security'], f'enmasse.fhir.sec.{test_suffix}')

        except ErrorReturnCode as error:
            stdout = error.stdout.decode('utf8')
            stderr = error.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception during outgoing FHIR import-export-reimport; stdout -> {stdout}')

        finally:
            for path in [import_path, export_path, reimport_export_path]:
                if os.path.exists(path):
                    os.remove(path)

            self._cleanup(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
