# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.odb.query.generic import OnPremGatewayWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.typing_ import anydict, list_

    gateway_def_list = list_[anydict]

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class OnPremGatewayExporter:
    """ Exports on-premises gateways to YAML.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export(self, session:'SASession', cluster_id:'int') -> 'gateway_def_list':
        """ Exports on-premises gateway definitions - a name, the flags and a list of
        addresses, which is everything the ODB stores about one.
        """
        logger.info('Exporting on-premises gateway definitions')

        # Our response to produce
        out = []

        wrapper = OnPremGatewayWrapper(session, cluster_id)

        rows = wrapper.get_list()

        for row in rows:

            gateway_def = {
                'name': row['name'],
                'is_active': row['is_active'],
                'is_key_reset_required': row['is_key_reset_required'],
                'hosts': row['hosts'],
            }

            out.append(gateway_def)

        gateway_count = len(out)

        logger.info('Successfully prepared %d on-premises gateway definitions for export', gateway_count)

        return out

# ################################################################################################################################
# ################################################################################################################################
