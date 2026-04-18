# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import importlib
import logging
import os
from unittest import TestCase, main

# Zato
from zato.common.enmasse_.exporter import EnmasseExporter
from zato.common.enmasse_.importer import EnmasseImporter
from zato.common.config.manager import ConfigManager

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Fields that are time-dependent and will change between roundtrips
_time_dependent_fields = frozenset(['start_date'])

# Fields that are generated randomly when missing and will differ between roundtrips
_random_fields = frozenset(['password', 'username'])

# ################################################################################################################################
# ################################################################################################################################

def _find_template_modules():
    """ Discovers all _template_*.py files in the enmasse test templates directory
    and returns a list of (module_name, template_variable_name, yaml_string) tuples.
    """
    out = []

    import zato.common.test.enmasse_ as enmasse_pkg
    templates_dir = os.path.dirname(enmasse_pkg.__file__)

    for filename in sorted(os.listdir(templates_dir)):
        if filename.startswith('_template_') and filename.endswith('.py'):
            module_name = filename[:-3]
            full_module = f'zato.common.test.enmasse_.{module_name}'

            mod = importlib.import_module(full_module)

            for attr_name in dir(mod):
                if attr_name.startswith('template_'):
                    value = getattr(mod, attr_name)
                    if isinstance(value, str) and value.strip():
                        out.append((full_module, attr_name, value))

    return out

# ################################################################################################################################
# ################################################################################################################################

def _get_sort_key(item):
    """ Returns a tuple of field names to use as a sort key for a dict item. """
    if 'name' in item:
        return ('name',)
    if 'security' in item:
        return ('security',)
    return None

# ################################################################################################################################
# ################################################################################################################################

def _normalize_for_comparison(data, skip_fields=None):
    """ Recursively normalize a dict/list structure for comparison,
    replacing skip_fields values with a placeholder and sorting
    lists of dicts by their 'name' field for order-independent comparison.
    """
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

class TestEnmasseRoundtrip(TestCase):

    def _do_import_export(self, yaml_string):
        """ Import a YAML string into a fresh ConfigManager via EnmasseImporter,
        then export it back via EnmasseExporter. Returns (config_manager, exported_dict, exported_yaml).
        """
        config_manager = ConfigManager()
        importer = EnmasseImporter(config_manager)
        importer.import_(yaml_string)

        exporter = EnmasseExporter(config_manager)
        exported_dict = exporter.export_to_dict()
        exported_yaml = exporter.export()

        return config_manager, exported_dict, exported_yaml

# ################################################################################################################################

    def test_all_templates_roundtrip(self):
        """ For every template YAML discovered, verify that:
        1. It can be imported and exported (round 1)
        2. The exported YAML can be re-imported and re-exported (round 2)
        3. Round 2 export matches round 1 export (idempotency)
        4. A third round also matches (stability)
        """

        templates = _find_template_modules()
        self.assertTrue(len(templates) > 0, 'No template YAML files found')

        skip_fields = _time_dependent_fields | _random_fields

        for module_name, var_name, yaml_string in templates:

            label = f'{module_name}.{var_name}'

            _, export_1_dict, export_1_yaml = self._do_import_export(yaml_string)

            self.assertTrue(
                len(export_1_dict) > 0,
                f'[{label}] Round 1 export produced empty dict'
            )

            _, export_2_dict, export_2_yaml = self._do_import_export(export_1_yaml)

            norm_1 = _normalize_for_comparison(export_1_dict, skip_fields)
            norm_2 = _normalize_for_comparison(export_2_dict, skip_fields)

            self.assertEqual(norm_1, norm_2,
                f'[{label}] Round 2 export differs from round 1 (not idempotent)')

            _, export_3_dict, _ = self._do_import_export(export_2_yaml)

            norm_3 = _normalize_for_comparison(export_3_dict, skip_fields)

            self.assertEqual(norm_2, norm_3,
                f'[{label}] Round 3 export differs from round 2 (unstable)')

# ################################################################################################################################

    def test_all_templates_section_preservation(self):
        """ Verify that every section present in the original YAML is also
        present after import+export roundtrip.
        """
        import yaml

        templates = _find_template_modules()
        self.assertTrue(len(templates) > 0, 'No template YAML files found')

        for module_name, var_name, yaml_string in templates:

            label = f'{module_name}.{var_name}'

            original = yaml.safe_load(yaml_string)
            if not original:
                continue

            _, exported_dict, _ = self._do_import_export(yaml_string)

            for section_key in original:
                self.assertIn(section_key, exported_dict,
                    f'[{label}] Section "{section_key}" from original YAML missing after roundtrip')

# ################################################################################################################################

    def test_all_templates_item_count_preservation(self):
        """ Verify that the number of items per section is preserved after roundtrip.
        """
        import yaml

        templates = _find_template_modules()
        self.assertTrue(len(templates) > 0, 'No template YAML files found')

        for module_name, var_name, yaml_string in templates:

            label = f'{module_name}.{var_name}'

            original = yaml.safe_load(yaml_string)
            if not original:
                continue

            _, exported_dict, _ = self._do_import_export(yaml_string)

            for section_key, original_items in original.items():
                if not isinstance(original_items, list):
                    continue

                exported_items = exported_dict.get(section_key, [])
                self.assertEqual(
                    len(original_items), len(exported_items),
                    f'[{label}] Section "{section_key}": expected {len(original_items)} items, got {len(exported_items)}'
                )

# ################################################################################################################################

    def test_all_templates_names_preserved(self):
        """ Verify that item names within each section survive the roundtrip.
        """
        import yaml

        templates = _find_template_modules()
        self.assertTrue(len(templates) > 0, 'No template YAML files found')

        for module_name, var_name, yaml_string in templates:

            label = f'{module_name}.{var_name}'

            original = yaml.safe_load(yaml_string)
            if not original:
                continue

            _, exported_dict, _ = self._do_import_export(yaml_string)

            for section_key, original_items in original.items():
                if not isinstance(original_items, list):
                    continue

                exported_items = exported_dict.get(section_key, [])

                original_names = {item.get('name') for item in original_items if 'name' in item}
                exported_names = {item.get('name') for item in exported_items if 'name' in item}

                if original_names:
                    self.assertEqual(original_names, exported_names,
                        f'[{label}] Section "{section_key}": name mismatch')

# ################################################################################################################################

    def test_re_export_yaml_string_stability(self):
        """ Verify that the parsed and normalized YAML is identical
        between round 2 and round 3 (stability after convergence).
        """
        import yaml

        templates = _find_template_modules()
        self.assertTrue(len(templates) > 0, 'No template YAML files found')

        skip_fields = _time_dependent_fields | _random_fields

        for module_name, var_name, yaml_string in templates:

            label = f'{module_name}.{var_name}'

            _, _, export_1_yaml = self._do_import_export(yaml_string)
            _, _, export_2_yaml = self._do_import_export(export_1_yaml)
            _, export_3_dict, _ = self._do_import_export(export_2_yaml)

            parsed_2 = yaml.safe_load(export_2_yaml)
            norm_2 = _normalize_for_comparison(parsed_2, skip_fields)
            norm_3 = _normalize_for_comparison(export_3_dict, skip_fields)

            self.assertEqual(norm_2, norm_3,
                f'[{label}] YAML not stable between round 2 and round 3')

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
