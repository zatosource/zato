# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
import os

# Zato
from zato.common.alerting.config_store import apply_type_config
from zato.common.alerting.notification_config import set_notification_config
from zato.common.alerting.seed import ensure_alerting_definitions
from zato.common.api import Alerting
from zato.common.rule_engine.sql import create_database_engine, create_schema, RuleSQLBackend
from zato.common.rule_engine.sql.constants import Default_DB_URL, Env_DB_URL

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import anydict, anylist, listtuple, stranydict

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# Who the rule store says made the changes
_actor = 'enmasse'

# The keys of an alert_rules entry that are not screen values
_entry_meta_keys = ('type', 'is_active')

# The YAML's notification keys mapped to the extra keys the sweep job carries -
# the YAML speaks the screen's vocabulary, so email addressing says email
# rather than the extra's own default_to and from.
yaml_to_extra = {
    'slack_webhook':    Alerting.Extra_Slack_Webhook,
    'teams_webhook':    Alerting.Extra_Teams_Webhook,
    'webhook_url':      Alerting.Extra_Webhook_URL,
    'email_connection': Alerting.Extra_Email_Connection,
    'email_to':         Alerting.Extra_Default_To,
    'email_from':       Alerting.Extra_From,
    'dashboard_url':    Alerting.Extra_Dashboard_URL,
}

# ################################################################################################################################
# ################################################################################################################################

def get_rule_backend() -> 'RuleSQLBackend':
    """ The typed SQL facade over the rule store, resolved through the same
    Env_DB_URL and Default_DB_URL the server's own get_backend uses.
    """
    # The URL is the same one the rule engine dashboard reads ..
    database_url = os.environ.get(Env_DB_URL)

    if not database_url:
        database_url = Default_DB_URL

    # .. an SQLite connection has to be shareable between threads ..
    if database_url.startswith('sqlite'):
        connection_options = {'check_same_thread': False}
        engine = create_database_engine(database_url, connect_args=connection_options)
    else:
        engine = create_database_engine(database_url)

    # The tables come into being on first run and every later call is a no-op
    create_schema(engine)

    out = RuleSQLBackend.from_engine(engine)
    return out

# ################################################################################################################################
# ################################################################################################################################

class AlertConfigImporter:
    """ A class that knows how to import alert rule thresholds and notification
    targets from YAML. The storage is the live rule documents and the sweep job's
    extra - the same places the config screen writes to, through the same helpers.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer

# ################################################################################################################################

    def sync_alert_rules(self, rule_list:'anylist', backend:'RuleSQLBackend | None'=None) -> 'listtuple':
        """ Synchronizes alert rule configuration from YAML with the rule store.

        Each entry names its type and carries screen-shaped values - the shared
        config_map helpers turn them into rule document updates, and only a document
        that actually changed is stored and published, so imports stay idempotent.
        """

        # Nothing to import means nothing to open the rule store for
        if not rule_list:
            return [], []

        if backend is None:
            backend = get_rule_backend()

        # A store the server never seeded gains the default definitions first,
        # so an import never depends on a server having run - re-seeding
        # an already-seeded store is a no-op.
        ensure_alerting_definitions(backend)

        # Rules are always updated in place, never created - the definitions
        # themselves come from the seed, the YAML only moves their values
        out_updated = []

        for entry in rule_list:

            type_name = entry['type']

            # Everything besides the entry's meta keys is a screen value
            values:'stranydict' = {}

            for key, value in entry.items():
                if key not in _entry_meta_keys:
                    values[key] = value

            changed = apply_type_config(
                backend,
                type_name,
                actor=_actor,
                values=values,
                is_active=entry.get('is_active'),
                comment=f'Imported alert config for type {type_name}',
            )

            if changed:
                out_updated.append(entry)
                logger.info('Updated alert rules for type %s', type_name)

        return [], out_updated

# ################################################################################################################################

    def sync_alert_notifications(self, values:'anydict', session:'SASession') -> 'bool':
        """ Synchronizes the notification targets from YAML with the sweep job's extra,
        through the same shared helper the config screen's save service uses.
        Returns whether anything actually changed.
        """

        # Nothing to import means nothing to write
        if not values:
            return False

        # The YAML speaks the screen's vocabulary - the extra keeps its own keys
        extra_values:'stranydict' = {}

        for yaml_key, extra_key in yaml_to_extra.items():
            if yaml_key in values:
                extra_values[extra_key] = values[yaml_key]

        changed = set_notification_config(session, self.importer.cluster_id, extra_values)

        if changed:
            session.commit()
            logger.info('Updated alert notification targets')

        return changed

# ################################################################################################################################
# ################################################################################################################################
