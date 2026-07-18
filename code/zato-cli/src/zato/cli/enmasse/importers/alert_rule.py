# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.alerting.model import AlertAction, Default_Dedup_Window_Seconds
from zato.common.api import Audit_Config
from zato.common.json_internal import dumps
from zato.common.odb.query.generic import GenericObjectWrapper

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import anydict, anylist, listtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

class AlertRuleImporter:
    """ A class that knows how to import alert rules from YAML.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.rule_defs = {}

# ################################################################################################################################

    def get_rules_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all alert rules from the database, keyed by name.
        """

        # Our response to produce
        out = {}

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Audit_Config.Type.Alert_Rule

        rows = wrapper.get_list()

        for row in rows:
            name = row['name']
            out[name] = {
                'id': row['id'],
                'name': name,
            }

        return out

# ################################################################################################################################

    def sync_alert_rules(self, rule_list:'anylist', session:'SASession') -> 'listtuple':
        """ Synchronizes alert rules from YAML with the database.

        Rules are updated in place, never deleted and recreated, so their ids stay stable
        for anything that references them.
        """

        # Lists of created and updated rules to report
        out_created = []
        out_updated = []

        db_rules = self.get_rules_from_db(session)

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Audit_Config.Type.Alert_Rule

        for rule in rule_list:

            name = rule['name']

            # The kind is the one required match field, everything else has a default
            rule_data = {
                'kind': rule['kind'],
                'source': rule.get('source', ''),
                'object_name': rule.get('object_name', ''),
                'action': rule.get('action', AlertAction.Email_Digest),
                'action_config': rule.get('action_config', {}),
                'dedup_window_seconds': rule.get('dedup_window_seconds', Default_Dedup_Window_Seconds),
                'is_active': rule.get('is_active', True),
            }

            # Serialize the rule body to its opaque form
            opaque = dumps(rule_data)

            if name in db_rules:

                # The rule exists so it is updated in place to keep its id stable
                rule_id = db_rules[name]['id']
                update = wrapper.update(name, opaque, id=rule_id)
                _ = session.execute(update)
                out_updated.append(rule)

                logger.info('Updated alert rule %s with id %s', name, rule_id)

            else:

                # The rule does not exist yet so it is created now ..
                insert = wrapper.create(name, opaque)
                _ = session.execute(insert)
                session.commit()

                # .. and read back to obtain its id.
                row = wrapper.get(name)
                rule_id = row['id']
                out_created.append(rule)

                logger.info('Created alert rule %s with id %s', name, rule_id)

            # Store the rule definition for name-to-id resolution
            self.rule_defs[name] = {
                'id': rule_id,
                'name': name,
            }

        session.commit()

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
