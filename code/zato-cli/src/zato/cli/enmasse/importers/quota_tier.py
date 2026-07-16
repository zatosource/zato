# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import Quota_Tiers
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

class QuotaTierImporter:
    """ A class that knows how to import quota tiers from YAML.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.tier_defs = {}

# ################################################################################################################################

    def get_tiers_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all quota tiers from the database, keyed by name.
        """

        # Our response to produce
        out = {}

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Quota_Tiers.Type.Quota_Tier

        rows = wrapper.get_list()

        for row in rows:
            name = row['name']
            out[name] = {
                'id': row['id'],
                'name': name,
            }

        return out

# ################################################################################################################################

    def sync_quota_tiers(self, tier_list:'anylist', session:'SASession') -> 'listtuple':
        """ Synchronizes quota tiers from YAML with the database.

        Tiers are updated in place, never deleted and recreated, because security definitions
        and groups reference them by id and the ids must remain stable.
        """

        # Lists of created and updated tiers to report
        out_created = []
        out_updated = []

        db_tiers = self.get_tiers_from_db(session)

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Quota_Tiers.Type.Quota_Tier

        for tier in tier_list:

            name = tier['name']
            description = tier.get('description', '')
            rules = tier.get('rules', [])

            # Serialize the tier body to its opaque form
            tier_data = {'description': description, 'rules': rules}
            opaque = dumps(tier_data)

            if name in db_tiers:

                # The tier exists so it is updated in place to keep its id stable
                tier_id = db_tiers[name]['id']
                update = wrapper.update(name, opaque, id=tier_id)
                _ = session.execute(update)
                out_updated.append(tier)

                logger.info('Updated quota tier %s with id %s', name, tier_id)

            else:

                # The tier does not exist yet so it is created now ..
                insert = wrapper.create(name, opaque)
                _ = session.execute(insert)
                session.commit()

                # .. and read back to obtain its id.
                row = wrapper.get(name)
                tier_id = row['id']
                out_created.append(tier)

                logger.info('Created quota tier %s with id %s', name, tier_id)

            # Store the tier definition for name-to-id resolution by other importers
            self.tier_defs[name] = {
                'id': tier_id,
                'name': name,
            }

        session.commit()

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
