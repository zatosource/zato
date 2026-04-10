# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import TestCase, main

# zato_server_core
from zato_server_core import ConfigStore

# Zato
from zato.cli.enmasse.importer import EnmasseYAMLImporter

# ################################################################################################################################
# ################################################################################################################################

class TestPubSubTopicImportSmoke(TestCase):

    def test_config_store_can_be_instantiated(self) -> 'None':
        store = ConfigStore()
        self.assertIsNotNone(store)

# ################################################################################################################################

    def test_enmasse_yaml_importer_can_be_instantiated(self) -> 'None':
        importer = EnmasseYAMLImporter()
        self.assertIsNotNone(importer)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':

    # stdlib
    import logging

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    _ = main()

# ################################################################################################################################
# ################################################################################################################################
