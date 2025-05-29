# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import HTTPSOAP, Service, to_json

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

class OutgoingRESTImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.connection_defs = {}

# ################################################################################################################################

    def get_outgoing_rest_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}
        logger.info('Retrieving outgoing REST connections from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP).filter(HTTPSOAP.cluster_id==cluster_id).filter(HTTPSOAP.connection==CONNECTION.OUTGOING).filter(HTTPSOAP.transport==URL_TYPE.PLAIN_HTTP) # type: ignore
        connections = to_json(query, return_as_dict=True)
        logger.info('Processing %d outgoing REST connections', len(connections))

        for item in connections:
            item = item['fields']
            name = item['name']
            logger.info('Processing outgoing REST connection: %s (id=%s)', name, item['id'])
            out[name] = item
            self.connection_defs[name] = item

        return out

# ################################################################################################################################

    def compare_outgoing_rest(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML outgoing REST connections with %d DB outgoing REST connections', len(yaml_defs), len(db_defs))

        for item in yaml_defs:
            name = item['name']
            logger.info('Checking YAML outgoing REST connection: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Outgoing REST connection %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Outgoing REST connection %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                for key, value in item.items():
                    if key in db_def and db_def[key] != value:
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
        return to_create, to_update

# ################################################################################################################################

    def create_outgoing_rest(self, outgoing_def:'anydict', session:'SASession') -> 'any_':
        name = outgoing_def['name']
        logger.info('Creating new outgoing REST connection: %s', name)

        outgoing = HTTPSOAP()
        outgoing.name = name
        outgoing.connection = CONNECTION.OUTGOING
        outgoing.transport = URL_TYPE.PLAIN_HTTP
        outgoing.cluster = self.importer.get_cluster(session)
        outgoing.is_active = True
        outgoing.is_internal = False
        outgoing.soap_action = 'not-used'

        # Set default values that may not be provided
        outgoing.ping_method = outgoing_def.get('ping_method', 'GET')
        outgoing.pool_size = outgoing_def.get('pool_size', 20)
        outgoing.timeout = outgoing_def.get('timeout', 60)
        outgoing.data_format = outgoing_def.get('data_format', 'json')

        for key, value in outgoing_def.items():
            if key not in ['service', 'security']:
                setattr(outgoing, key, value)

        if 'security' in outgoing_def:
            security_name = outgoing_def['security']
            if security_name not in self.importer.sec_defs:
                error_msg = f'Security definition "{security_name}" not found for outgoing REST connection "{name}"'
                logger.error(error_msg)
                raise Exception(error_msg)
            sec_def = self.importer.sec_defs[security_name]
            outgoing.security_id = sec_def['id']

        session.add(outgoing)
        self.connection_defs[name] = outgoing
        return outgoing

# ################################################################################################################################

    def update_outgoing_rest(self, outgoing_def:'anydict', session:'SASession') -> 'any_':
        outgoing_id = outgoing_def['id']
        name = outgoing_def['name']
        logger.info('Updating outgoing REST connection: %s (id=%s)', name, outgoing_id)

        outgoing = session.query(HTTPSOAP).filter_by(id=outgoing_id).one()

        for key, value in outgoing_def.items():
            if key not in ['id', 'service', 'security']:
                setattr(outgoing, key, value)

        if 'security' in outgoing_def:
            security_name = outgoing_def['security']
            if security_name not in self.importer.sec_defs:
                error_msg = f'Security definition "{security_name}" not found for outgoing REST connection "{name}"'
                logger.error(error_msg)
                raise Exception(error_msg)
            sec_def = self.importer.sec_defs[security_name]
            outgoing.security_id = sec_def['id']

        session.add(outgoing)
        self.connection_defs[name] = outgoing
        return outgoing

# ################################################################################################################################

    def sync_outgoing_rest(self, outgoing_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d outgoing REST connections from YAML', len(outgoing_list))

        db_outgoing = self.get_outgoing_rest_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_outgoing_rest(outgoing_list, db_outgoing)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new outgoing REST connections', len(to_create))
            for item in to_create:
                logger.info('Creating outgoing REST connection: name=%s', item['name'])
                instance = self.create_outgoing_rest(item, session)
                logger.info('Created outgoing REST connection: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

            logger.info('Updating %d existing outgoing REST connections', len(to_update))
            for item in to_update:
                logger.info('Updating outgoing REST connection: name=%s id=%s', item['name'], item['id'])
                instance = self.update_outgoing_rest(item, session)
                logger.info('Updated outgoing REST connection: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing outgoing REST connections: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
