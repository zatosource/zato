# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import Audit_Config
from zato.common.odb.query.generic import GenericObjectWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    rule_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AlertRuleExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'rule_def_list':
        """ Exports alert rule definitions.
        """
        logger.info('Exporting alert rule definitions')

        wrapper = GenericObjectWrapper(session, cluster_id)
        wrapper.type_ = Audit_Config.Type.Alert_Rule

        rows = wrapper.get_list()

        exported_rules = []

        for row in rows:

            # Rows written before the collector config existed do not carry the key
            if 'config' in row:
                config = row['config']
            else:
                config = {}

            rule_def = {
                'name': row['name'],
                'kind': row['kind'],
                'source': row['source'],
                'object_name': row['object_name'],
                'action': row['action'],
                'action_config': row['action_config'],
                'config': config,
                'dedup_window_seconds': row['dedup_window_seconds'],
                'is_active': row['is_active'],
            }

            exported_rules.append(rule_def)

        logger.info('Successfully prepared %d alert rule definitions for export', len(exported_rules))

        return exported_rules

# ################################################################################################################################
# ################################################################################################################################
