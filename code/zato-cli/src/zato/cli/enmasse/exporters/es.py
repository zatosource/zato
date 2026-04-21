# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import GENERIC
from zato.common.odb.model import to_json
from zato.common.odb.query import search_es_list
from zato.common.util.sql import parse_instance_opaque_attr

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import list_

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class ElasticSearchExporter:
    """ Exports ElasticSearch connection definitions to a YAML-compatible dictionary.
    """
    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

    # Fields stored directly in the database model
    DIRECT_FIELDS = [
        'id',
        'name',
        'is_active',
        'hosts',
        'timeout',
        'body_as',
    ]

# ################################################################################################################################

    def export_es(self, session:'SASession') -> 'list_':
        """ Exports all ElasticSearch connection definitions to a YAML-compatible dictionary.
        """
        logger.info('Exporting ElasticSearch connection definitions')

        # Get the cluster ID from the parent
        cluster_id = self.exporter.cluster_id

        # Get all ElasticSearch connection definitions from the database
        es_list = search_es_list(session, cluster_id)

        if not es_list:
            logger.info('No ElasticSearch connection definitions found in DB')
            return []

        # Convert the search results to a list of dictionaries
        es_definitions = to_json(es_list, return_as_dict=True)
        logger.debug('Processing %d ElasticSearch connection definitions', len(es_definitions))

        out = []

        for es_item in es_definitions:

            if GENERIC.ATTR_NAME in es_item:
                opaque = parse_instance_opaque_attr(es_item)
                es_item.update(opaque)
                del es_item[GENERIC.ATTR_NAME]

            item = {
                'name': es_item['name'],
                'hosts': es_item['hosts'],
                'is_active': es_item['is_active'],
                'body_as': es_item['body_as']
            }

            if (timeout := es_item.get('timeout')) and timeout != 90:
                item['timeout'] = timeout

            out.append(item)

        logger.info('Successfully prepared %d ElasticSearch connection definitions for export', len(out))

        return out

# ################################################################################################################################
# ################################################################################################################################
