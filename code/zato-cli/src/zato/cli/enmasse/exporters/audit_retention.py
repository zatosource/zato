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

    policy_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AuditRetentionExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'policy_def_list':
        """ Exports audit retention policy definitions.
        """
        logger.info('Exporting audit retention policy definitions')

        wrapper = GenericObjectWrapper(session, cluster_id)
        wrapper.type_ = Audit_Config.Type.Retention_Policy

        rows = wrapper.get_list()

        exported_policies = []

        for row in rows:

            policy_def = {
                'name': row['name'],
                'retention_days': row['retention_days'],
                'content_retention_days': row['content_retention_days'],
                'archive_dir': row['archive_dir'],
            }

            exported_policies.append(policy_def)

        logger.info('Successfully prepared %d retention policy definitions for export', len(exported_policies))

        return exported_policies

# ################################################################################################################################
# ################################################################################################################################
