# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from unittest import main

# Zato
from zato.common.test import rand_string, rand_unicode
from zato.common.test.enmasse_.base import BaseEnmasseTestCase
from zato.common.test.enmasse_._template_complex_01 import template_complex_01
from zato.common.util.open_ import open_w

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class EnmasseTestCase(BaseEnmasseTestCase):

    def get_smtp_config(self) -> 'str':
        return ''

    def _cleanup(self, test_suffix:'str') -> 'None':

        # Clean up test data
        from zato.cli.enmasse.client import cleanup_enmasse
        cleanup_enmasse()

# ################################################################################################################################

    def _test_enmasse_ok(self, template:'str') -> 'None':

        # sh
        from sh import ErrorReturnCode

        # We don't want to require a server
        os.environ['Zato_Needs_Config_Reload'] = 'False'

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        file_name = 'zato-enmasse-' + test_suffix + '.yaml'
        config_path = os.path.join(tmp_dir, file_name)

        smtp_config = self.get_smtp_config()

        data = template.format(test_suffix=test_suffix, smtp_config=smtp_config)

        f = open_w(config_path)
        _ = f.write(data)
        f.close()

        try:
            # Invoke enmasse to create objects ..
            _ = self.invoke_enmasse(config_path)

            # .. now invoke it again to edit them in place.
            _ = self.invoke_enmasse(config_path)

        except ErrorReturnCode as e:
            stdout:'bytes' = e.stdout # type: bytes
            stdout = stdout.decode('utf8') # type: ignore
            stderr:'str' = e.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception while invoking enmasse; stdout -> {stdout}')

        finally:
            self._cleanup(test_suffix)

# ################################################################################################################################

    def test_enmasse_complex_ok_01(self) -> 'None':
        self._test_enmasse_ok(template_complex_01)

# ################################################################################################################################

    def test_enmasse_import_export_flow(self) -> 'None':
        """ Test a complete import-export flow to verify data consistency.
        """

        # sh
        from sh import ErrorReturnCode

        # PyYAML
        import yaml

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        # Create file names for import and export
        import_file_name = 'zato-enmasse-import-' + test_suffix + '.yaml'
        export_file_name = 'zato-enmasse-export-' + test_suffix + '.yaml'

        import_path = os.path.join(tmp_dir, import_file_name)
        export_path = os.path.join(tmp_dir, export_file_name)

        # Prepare the initial import file
        smtp_config = self.get_smtp_config()
        data = template_complex_01.format(test_suffix=test_suffix, smtp_config=smtp_config)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:
            # First import the data
            _ = self.invoke_enmasse(import_path)

            # Now export the data
            include_types = 'channel_rest,security,elastic_search,channel_openapi,channel_hl7_mllp'
            _ = self.invoke_enmasse(export_path, is_import=False, is_export=True, include_type=include_types)

            # Read back both files
            with open(import_path, 'r') as f:
                import_data = f.read()


            with open(export_path, 'r') as f:
                export_data = f.read()

            _ = yaml.safe_load(import_data)
            exported_dict = yaml.safe_load(export_data)

            # Verify that rate_limiting survived the round trip for channels
            if exported_dict and 'channel_rest' in exported_dict:
                exported_channels_by_name = {}

                for channel in exported_dict['channel_rest']:
                    exported_channels_by_name[channel['name']] = channel

                # enmasse.channel.rest.2 should have rate_limiting
                channel_2_name = f'enmasse.channel.rest.2.{test_suffix}'
                if channel_2_name in exported_channels_by_name:
                    channel_2 = exported_channels_by_name[channel_2_name]
                    self.assertIn('rate_limiting', channel_2, f'rate_limiting missing from exported {channel_2_name}')
                    self.assertEqual(len(channel_2['rate_limiting']), 1)

            # Verify that HL7 MLLP channels survived the round trip
            if exported_dict:
                if 'channel_hl7_mllp' in exported_dict:
                    exported_hl7_channels = exported_dict['channel_hl7_mllp']

                    # Filter to only enmasse test channels
                    enmasse_hl7_channels = []
                    for channel in exported_hl7_channels:
                        if channel['name'].startswith('enmasse.hl7.mllp.'):
                            enmasse_hl7_channels.append(channel)

                    enmasse_channel_count = len(enmasse_hl7_channels)
                    self.assertEqual(enmasse_channel_count, 3,
                        f'Expected 3 HL7 MLLP channels, found {enmasse_channel_count}')

            # Verify that rate_limiting survived the round trip for security
            if exported_dict and 'security' in exported_dict:
                exported_security_by_name = {}

                for sec_def in exported_dict['security']:
                    exported_security_by_name[sec_def['name']] = sec_def

                # enmasse.basic_auth.1 should have rate_limiting
                basic_auth_1_name = f'enmasse.basic_auth.1.{test_suffix}'
                if basic_auth_1_name in exported_security_by_name:
                    basic_auth_1 = exported_security_by_name[basic_auth_1_name]
                    self.assertIn('rate_limiting', basic_auth_1, f'rate_limiting missing from exported {basic_auth_1_name}')
                    self.assertEqual(len(basic_auth_1['rate_limiting']), 1)

        except ErrorReturnCode as e:
            stdout = e.stdout.decode('utf8')
            stderr = e.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception during import-export flow; stdout -> {stdout}')

        finally:
            # Clean up test files
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(export_path):
                os.remove(export_path)

            self._cleanup(test_suffix)

# ################################################################################################################################

    def test_enmasse_with_env_file(self) -> 'None':
        """Test enmasse with environment variables loaded from a file."""

        # sh
        from sh import ErrorReturnCode

        tmp_dir = gettempdir()
        test_suffix = rand_unicode() + '.' + rand_string()

        # Create file names for import and env file
        import_file_name = 'zato-enmasse-import-' + test_suffix + '.yaml'
        env_file_name = 'zato-enmasse-env-' + test_suffix + '.ini'

        import_path = os.path.join(tmp_dir, import_file_name)
        env_path = os.path.join(tmp_dir, env_file_name)

        # Create environment variables file
        env_content = """[env]
BasicAuth1 = secret-password-1
BasicAuth2 = secret-password-2
EnmasseApiKey1 = api-key-value-1
"""

        with open_w(env_path) as f:
            _ = f.write(env_content)

        # Prepare the import data with placeholders for env vars
        data = template_complex_01.format(test_suffix=test_suffix)

        with open_w(import_path) as f:
            _ = f.write(data)

        try:
            # Invoke the command with env file
            from zato.common.util.cli import get_zato_sh_command
            command = get_zato_sh_command()

            # Custom invocation to include env-file
            from zato.common.test.config import TestConfig
            out = command('enmasse', TestConfig.server_location,
                '--import',
                '--input', import_path,
                '--verbose',
                '--env-file', env_path
            ) # type: ignore

            # Check for successful import
            self.assertEqual(out.exit_code, 0)

            # Convert output to string for inspection
            stdout = out.stdout.decode('utf8')

            # Look for success message in output
            self.assertIn('⭐ Enmasse OK', stdout)

        except ErrorReturnCode as e:
            stdout = e.stdout.decode('utf8')
            stderr = e.stderr

            self._warn_on_error(stdout, stderr)
            self.fail(f'Caught an exception with env file; stdout -> {stdout}')

        finally:

            # Clean up test files
            if os.path.exists(import_path):
                os.remove(import_path)
            if os.path.exists(env_path):
                os.remove(env_path)

            self._cleanup(test_suffix)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
