# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.cli.enmasse.util import preprocess_item
from zato.common.api import CONNECTION, MISC, URL_TYPE
from zato.common.odb.model import HTTPSOAP, to_json
from zato.common.util.sql import set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

# What a YAML definition means when it does not say otherwise.
_default_is_active = True
_default_is_internal = False
_default_url_path = '/'

# ################################################################################################################################
# ################################################################################################################################

class OutgoingAS4Importer:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.connection_defs:'anydict' = {}

# ################################################################################################################################

    def get_outgoing_as4_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':

        # Our response to produce
        out:'anydict' = {}

        logger.info('Retrieving outgoing AS4 connections from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP)
        query = query.filter(HTTPSOAP.cluster_id==cluster_id)
        query = query.filter(HTTPSOAP.connection==CONNECTION.OUTGOING)
        query = query.filter(HTTPSOAP.transport==URL_TYPE.AS4)

        connections = to_json(query, return_as_dict=True)
        logger.info('Processing %d outgoing AS4 connections', len(connections))

        for item in connections:
            item = item['fields']
            name = item['name']
            logger.info('Processing outgoing AS4 connection: %s (id=%s)', name, item['id'])

            # Unpack opaque attributes into top-level keys so comparisons see the AS4 fields
            # like the profile, party ids or the pasted PEM keystore material.
            if opaque1 := item.get('opaque1'):
                opaque = loads(opaque1)
                if opaque:
                    item.update(opaque)

            out[name] = item
            self.connection_defs[name] = item

        return out

# ################################################################################################################################

    def compare_outgoing_as4(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create:'anylist' = []
        to_update:'anylist' = []

        logger.info('Comparing %d YAML outgoing AS4 connections with %d DB outgoing AS4 connections', len(yaml_defs), len(db_defs))

        for item in yaml_defs:
            item = preprocess_item(item)

            name = item['name']
            logger.info('Checking YAML outgoing AS4 connection: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Outgoing AS4 connection %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Outgoing AS4 connection %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                # Compare standard attributes - the AS4 fields were already unpacked
                # from opaque attributes into the top-level DB keys.
                for key, value in item.items():

                    # A field the database row does not have yet means an update too.
                    if key not in db_def:
                        logger.info('Field %s.%s not in DB yet, will update', name, key)
                        needs_update = True
                        break

                    if db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                if needs_update:
                    item['id'] = db_def['id']
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))

        out = to_create, to_update
        return out

# ################################################################################################################################

    def create_outgoing_as4(self, outgoing_def:'anydict', session:'SASession') -> 'any_':
        name = outgoing_def['name']
        logger.info('Creating outgoing AS4 connection: %s', name)

        outgoing = HTTPSOAP()

        outgoing.name = name
        outgoing.is_active = outgoing_def.get('is_active', _default_is_active)
        outgoing.connection = CONNECTION.OUTGOING
        outgoing.transport = URL_TYPE.AS4
        outgoing.cluster = self.importer.get_cluster(session)
        outgoing.is_internal = outgoing_def.get('is_internal', _default_is_internal)
        outgoing.url_path = outgoing_def.get('url_path', _default_url_path)
        outgoing.soap_action = ''
        outgoing.timeout = outgoing_def.get('timeout', MISC.DEFAULT_HTTP_TIMEOUT)

        # Copy other defined attributes - the AS4 fields are not columns,
        # they travel to the opaque attributes below.
        for key, value in outgoing_def.items():
            setattr(outgoing, key, value)

        # A TLS validation toggle that is absent means TLS is validated.
        if 'validate_tls' not in outgoing_def:
            outgoing_def = dict(outgoing_def)
            outgoing_def['validate_tls'] = True

        set_instance_opaque_attrs(outgoing, outgoing_def)

        session.add(outgoing)
        self.connection_defs[name] = outgoing

        return outgoing

# ################################################################################################################################

    def update_outgoing_as4(self, outgoing_def:'anydict', session:'SASession') -> 'any_':
        outgoing_id = outgoing_def['id']
        name = outgoing_def['name']
        logger.info('Updating outgoing AS4 connection: %s (id=%s)', name, outgoing_id)

        outgoing = session.query(HTTPSOAP).filter_by(id=outgoing_id).one()

        for key, value in outgoing_def.items():
            setattr(outgoing, key, value)

        # Fields that are not columns go into the opaque attributes,
        # merged with whatever the row already keeps there.
        set_instance_opaque_attrs(outgoing, outgoing_def)

        session.add(outgoing)
        self.connection_defs[name] = outgoing

        return outgoing

# ################################################################################################################################

    def sync_outgoing_as4(self, outgoing_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d outgoing AS4 connections from YAML', len(outgoing_list))

        db_outgoing = self.get_outgoing_as4_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_outgoing_as4(outgoing_list, db_outgoing)

        out_created:'anylist' = []
        out_updated:'anylist' = []

        try:
            logger.info('Creating %d new outgoing AS4 connections', len(to_create))
            for item in to_create:
                logger.info('Creating outgoing AS4 connection: name=%s', item['name'])
                instance = self.create_outgoing_as4(item, session)
                logger.info('Created outgoing AS4 connection: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

            logger.info('Updating %d existing outgoing AS4 connections', len(to_update))
            for item in to_update:
                logger.info('Updating outgoing AS4 connection: name=%s id=%s', item['name'], item['id'])
                instance = self.update_outgoing_as4(item, session)
                logger.info('Updated outgoing AS4 connection: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        # A genuinely broad boundary - whatever failed while syncing,
        # the session must be rolled back before the error propagates.
        except Exception as e:
            logger.error('Error syncing outgoing AS4 connections: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        out = out_created, out_updated
        return out

# ################################################################################################################################
# ################################################################################################################################
