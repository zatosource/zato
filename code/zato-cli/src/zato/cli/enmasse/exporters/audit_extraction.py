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

    extraction_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AuditExtractionExporter:

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'extraction_def_list':
        """ Exports attribute-extraction rule set definitions.
        """
        logger.info('Exporting extraction rule set definitions')

        wrapper = GenericObjectWrapper(session, cluster_id)
        wrapper.type_ = Audit_Config.Type.Extraction_Rules

        rows = wrapper.get_list()

        exported_extraction = []

        for row in rows:

            extraction_def = {
                'name': row['name'],
                'source': row['source'],
                'rules': row['rules'],
            }

            exported_extraction.append(extraction_def)

        logger.info('Successfully prepared %d extraction rule set definitions for export', len(exported_extraction))

        return exported_extraction

# ################################################################################################################################
# ################################################################################################################################
