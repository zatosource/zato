# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.alerting import config_map
from zato.common.alerting.config_store import get_type_definition
from zato.common.alerting.notification_config import read_notification_config
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.api import Alerting
from zato.common.odb.model import Job
from zato.common.rule_engine.sql.constants import Documents_Key
from zato.common.rule_engine.sql.document import deserialize_document

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.exporter import EnmasseYAMLExporter
    from zato.common.rule_engine.sql import RuleSQLBackend
    from zato.common.typing_ import anydict, anylist

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# The extra keys the sweep job carries mapped to the YAML's own notification keys -
# the reverse of what the importer applies, so an export re-imports without changes.
extra_to_yaml = {
    Alerting.Extra_Slack_Webhook:    'slack_webhook',
    Alerting.Extra_Teams_Webhook:    'teams_webhook',
    Alerting.Extra_Webhook_URL:      'webhook_url',
    Alerting.Extra_Email_Connection: 'email_connection',
    Alerting.Extra_Default_To:       'email_to',
    Alerting.Extra_From:             'email_from',
    Alerting.Extra_Dashboard_URL:    'dashboard_url',
}

# ################################################################################################################################
# ################################################################################################################################

class AlertConfigExporter:
    """ Exports alert rule thresholds and notification targets - the live rule
    documents and the sweep job's extra read through the same shared helpers
    the config screen reads through, in the screen's own vocabulary and units.
    """

    def __init__(self, exporter:'EnmasseYAMLExporter') -> 'None':
        self.exporter = exporter

# ################################################################################################################################

    def export_rules(self, backend:'RuleSQLBackend') -> 'anylist':
        """ Exports each alert type's configuration - its active state and its
        screen-shaped values, one entry per type, in the screen's row order.
        """
        logger.info('Exporting alert rule configuration')

        # A store the server never seeded gains the default definitions first,
        # so an export always mirrors what the config screen would show.
        ensure_alerting_definitions(backend)

        # Our response to produce
        out = []

        for type_name in config_map.type_to_ruleset:

            definition = get_type_definition(backend, type_name)

            document = deserialize_document(definition.document)
            documents = document[Documents_Key]

            entry:'anydict' = {'type': type_name}
            entry['is_active'] = config_map.is_type_active(documents)
            entry.update(config_map.read_type_values(type_name, documents))

            out.append(entry)

        logger.info('Successfully prepared %d alert rule entries for export', len(out))

        return out

# ################################################################################################################################

    def export_notifications(self, session:'SASession', cluster_id:'int') -> 'anydict':
        """ Exports the notification targets the sweep job's extra holds, keyed
        by the YAML's own names - a target never filled in is left out entirely.
        """
        logger.info('Exporting alert notification targets')

        job = session.query(Job).\
            filter(Job.name==Alerting.Job_Name).\
            filter(Job.cluster_id==cluster_id).\
            first()

        # An environment whose servers never ran has no sweep job yet,
        # which simply means no targets were ever configured.
        if job is None:
            return {}

        values = read_notification_config(job.extra)

        # Our response to produce
        out:'anydict' = {}

        for extra_key, yaml_key in extra_to_yaml.items():
            value = values[extra_key]
            if value:
                out[yaml_key] = value

        return out

# ################################################################################################################################
# ################################################################################################################################
