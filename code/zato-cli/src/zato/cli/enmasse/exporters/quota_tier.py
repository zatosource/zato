# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import Quota_Tiers
from zato.common.odb.query.generic import GenericObjectWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    tier_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class QuotaTierExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'tier_def_list':
        """ Exports quota tier definitions.
        """
        logger.info('Exporting quota tier definitions')

        wrapper = GenericObjectWrapper(session, cluster_id)
        wrapper.type_ = Quota_Tiers.Type.Quota_Tier

        rows = wrapper.get_list()

        exported_tiers = []

        for row in rows:

            tier_def = {
                'name': row['name'],
                'description': row['description'],
                'rules': row['rules'],
            }

            exported_tiers.append(tier_def)

        logger.info('Successfully prepared %d quota tier definitions for export', len(exported_tiers))

        return exported_tiers

# ################################################################################################################################
# ################################################################################################################################
