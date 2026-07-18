# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
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

class AuditRetentionImporter:
    """ A class that knows how to import audit retention policies from YAML.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.policy_defs = {}

# ################################################################################################################################

    def get_policies_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all retention policies from the database, keyed by name.
        """

        # Our response to produce
        out = {}

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Audit_Config.Type.Retention_Policy

        rows = wrapper.get_list()

        for row in rows:
            name = row['name']
            out[name] = {
                'id': row['id'],
                'name': name,
            }

        return out

# ################################################################################################################################

    def sync_retention_policies(self, policy_list:'anylist', session:'SASession') -> 'listtuple':
        """ Synchronizes retention policies from YAML with the database.

        Policies are updated in place, never deleted and recreated, so their ids stay stable.
        """

        # Lists of created and updated policies to report
        out_created = []
        out_updated = []

        db_policies = self.get_policies_from_db(session)

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Audit_Config.Type.Retention_Policy

        for policy in policy_list:

            name = policy['name']

            # Both retention tiers plus the optional archive directory
            policy_data = {
                'retention_days': policy['retention_days'],
                'content_retention_days': policy.get('content_retention_days', 0),
                'archive_dir': policy.get('archive_dir', ''),
            }

            # Serialize the policy body to its opaque form
            opaque = dumps(policy_data)

            if name in db_policies:

                # The policy exists so it is updated in place to keep its id stable
                policy_id = db_policies[name]['id']
                update = wrapper.update(name, opaque, id=policy_id)
                _ = session.execute(update)
                out_updated.append(policy)

                logger.info('Updated retention policy %s with id %s', name, policy_id)

            else:

                # The policy does not exist yet so it is created now ..
                insert = wrapper.create(name, opaque)
                _ = session.execute(insert)
                session.commit()

                # .. and read back to obtain its id.
                row = wrapper.get(name)
                policy_id = row['id']
                out_created.append(policy)

                logger.info('Created retention policy %s with id %s', name, policy_id)

            # Store the policy definition for name-to-id resolution
            self.policy_defs[name] = {
                'id': policy_id,
                'name': name,
            }

        session.commit()

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
