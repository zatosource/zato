# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys
import yaml
from logging import basicConfig, getLogger, WARN
from tempfile import gettempdir
from unittest import main, TestCase

# Zato
from zato.common.test.config import TestConfig

# ################################################################################################################################
# ################################################################################################################################

basicConfig(level=WARN, format='%(asctime)s - %(message)s')
logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

_time_dependent_fields = frozenset(['start_date'])
_random_fields = frozenset(['password', 'username'])

# Sections without a natural key that get duplicated on re-import
_skip_sections = frozenset(['pubsub_permission', 'pubsub_subscription'])

# ################################################################################################################################
# ################################################################################################################################

def _is_server_running():
    """ Check if a Zato server is running by attempting a TCP connection. """
    import socket
    try:
        with socket.create_connection(('localhost', 17010), timeout=2):
            return True
    except (ConnectionRefusedError, OSError, socket.timeout):
        return False

# ################################################################################################################################
# ################################################################################################################################

def _get_sort_key(item):
    if 'name' in item:
        return ('name',)
    if 'security' in item:
        return ('security',)
    return None

def _normalize_for_comparison(data, skip_fields=None):
    skip_fields = skip_fields or set()

    if isinstance(data, dict):
        return {
            k: '<SKIPPED>' if k in skip_fields else _normalize_for_comparison(v, skip_fields)
            for k, v in sorted(data.items())
        }

    elif isinstance(data, list):
        normalized = [_normalize_for_comparison(item, skip_fields) for item in data]
        if normalized and isinstance(normalized[0], dict):
            sort_key = _get_sort_key(normalized[0])
            if sort_key:
                normalized.sort(key=lambda x: tuple(str(x.get(k, '')) for k in sort_key))
        return normalized

    else:
        return data

# ################################################################################################################################
# ################################################################################################################################

class TestEnmasseCLI(TestCase):

    @classmethod
    def setUpClass(cls):
        if not _is_server_running():
            from unittest import SkipTest
            msg = 'ZATO ENMASSE CLI TESTS SKIPPED SERVER NOT RUNNING'
            print(f'\n\n    {msg}\n', file=sys.stderr)
            raise SkipTest(msg)

    def _invoke_enmasse(self, *extra_args):
        """ Invoke the zato enmasse CLI command. """
        from sh import ErrorReturnCode
        from zato.common.util.cli import get_zato_sh_command
        command = get_zato_sh_command()
        args = ['enmasse', TestConfig.server_location, '--verbose'] + list(extra_args)
        try:
            out = command(*args)
        except ErrorReturnCode as e:
            stdout = e.stdout.decode('utf8') if isinstance(e.stdout, bytes) else str(e.stdout)
            self.fail(f'enmasse failed (exit {e.exit_code}): {stdout[:500]}')
        self.assertEqual(out.exit_code, 0, f'enmasse failed: {out.stderr}')
        return out

    def _import_file(self, path):
        return self._invoke_enmasse('--import', '--input', path)

    def _export_file(self, path):
        return self._invoke_enmasse('--export', '--output', path)

    def _read_yaml(self, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f.read())

    def test_cli_roundtrip(self):
        """ Import via CLI, export, re-import the export, re-export, compare.
        Then do it once more and compare again.
        """
        from zato.common.test.enmasse_._template_complex_01 import template_complex_01

        tmp_dir = gettempdir()
        input_path = os.path.join(tmp_dir, 'zato-enmasse-cli-input.yaml')
        export_1_path = os.path.join(tmp_dir, 'zato-enmasse-cli-export-1.yaml')
        export_2_path = os.path.join(tmp_dir, 'zato-enmasse-cli-export-2.yaml')
        export_3_path = os.path.join(tmp_dir, 'zato-enmasse-cli-export-3.yaml')

        skip_fields = _time_dependent_fields | _random_fields

        try:

            with open(input_path, 'w') as f:
                _ = f.write(template_complex_01)

            # Round 1: import original, export
            self._import_file(input_path)
            self._export_file(export_1_path)

            data_1 = self._read_yaml(export_1_path)
            self.assertTrue(data_1, 'Round 1 export is empty')

            original_sections = set(yaml.safe_load(template_complex_01).keys())
            for section in original_sections - _skip_sections:
                self.assertIn(section, data_1, f'Section "{section}" missing from export')

            # Round 2: re-import the export, re-export
            self._import_file(export_1_path)
            self._export_file(export_2_path)

            data_2 = self._read_yaml(export_2_path)
            self.assertTrue(data_2, 'Round 2 export is empty')

            data_1_filtered = {k: v for k, v in data_1.items() if k not in _skip_sections}
            data_2_filtered = {k: v for k, v in data_2.items() if k not in _skip_sections}

            norm_1 = _normalize_for_comparison(data_1_filtered, skip_fields)
            norm_2 = _normalize_for_comparison(data_2_filtered, skip_fields)

            self.assertEqual(norm_1, norm_2, 'Round 2 export differs from round 1 (not idempotent)')

            # Round 3: re-import again, re-export again
            self._import_file(export_2_path)
            self._export_file(export_3_path)

            data_3 = self._read_yaml(export_3_path)
            data_3_filtered = {k: v for k, v in data_3.items() if k not in _skip_sections}

            norm_3 = _normalize_for_comparison(data_3_filtered, skip_fields)

            self.assertEqual(norm_2, norm_3, 'Round 3 export differs from round 2 (unstable)')

        finally:
            for p in (input_path, export_1_path, export_2_path, export_3_path):
                if os.path.exists(p):
                    os.remove(p)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
