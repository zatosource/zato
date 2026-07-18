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

class AuditExtractionImporter:
    """ A class that knows how to import attribute-extraction rule sets from YAML.
    Each set is named after the channel or connection it applies to and holds
    the declarative rules extracting searchable attributes out of messages.
    """

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.extraction_defs = {}

# ################################################################################################################################

    def get_extraction_from_db(self, session:'SASession') -> 'anydict':
        """ Returns all extraction rule sets from the database, keyed by name.
        """

        # Our response to produce
        out = {}

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Audit_Config.Type.Extraction_Rules

        rows = wrapper.get_list()

        for row in rows:
            name = row['name']
            out[name] = {
                'id': row['id'],
                'name': name,
            }

        return out

# ################################################################################################################################

    def sync_extraction_rules(self, extraction_list:'anylist', session:'SASession') -> 'listtuple':
        """ Synchronizes extraction rule sets from YAML with the database.

        Sets are updated in place, never deleted and recreated, so their ids stay stable.
        """

        # Lists of created and updated sets to report
        out_created = []
        out_updated = []

        db_extraction = self.get_extraction_from_db(session)

        wrapper = GenericObjectWrapper(session, self.importer.cluster_id)
        wrapper.type_ = Audit_Config.Type.Extraction_Rules

        for extraction in extraction_list:

            name = extraction['name']

            # The audit source the set applies to and the rules themselves -
            # each rule is a dict of attr_name, rule_type and expression.
            extraction_data = {
                'source': extraction.get('source', ''),
                'rules': extraction['rules'],
            }

            # Serialize the set body to its opaque form
            opaque = dumps(extraction_data)

            if name in db_extraction:

                # The set exists so it is updated in place to keep its id stable
                extraction_id = db_extraction[name]['id']
                update = wrapper.update(name, opaque, id=extraction_id)
                _ = session.execute(update)
                out_updated.append(extraction)

                logger.info('Updated extraction rule set %s with id %s', name, extraction_id)

            else:

                # The set does not exist yet so it is created now ..
                insert = wrapper.create(name, opaque)
                _ = session.execute(insert)
                session.commit()

                # .. and read back to obtain its id.
                row = wrapper.get(name)
                extraction_id = row['id']
                out_created.append(extraction)

                logger.info('Created extraction rule set %s with id %s', name, extraction_id)

            # Store the set definition for name-to-id resolution
            self.extraction_defs[name] = {
                'id': extraction_id,
                'name': name,
            }

        session.commit()

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
