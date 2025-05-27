# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging

# Zato
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

class ChannelImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer

# ################################################################################################################################

    def get_rest_channels_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}
        logger.info('Retrieving REST channels from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP).filter(HTTPSOAP.cluster_id==cluster_id).filter(HTTPSOAP.connection=='channel').filter(HTTPSOAP.transport=='plain_http') # type: ignore
        channels = to_json(query, return_as_dict=True)
        logger.info('Processing %d REST channels', len(channels))

        for item in channels:
            item = item['fields']
            name = item['name']
            logger.info('Processing channel: %s (id=%s)', name, item['id'])
            out[name] = item

        return out

# ################################################################################################################################

    def compare_channel_rest(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML channels with %d DB channels', len(yaml_defs), len(db_defs))

        for item in yaml_defs:
            name = item['name']
            logger.info('Checking YAML channel: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Channel %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Channel %s exists in DB with id=%s', name, db_def['id'])

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

    def create_channel_rest(self, channel_def:'anydict', session:'SASession') -> 'any_':
        name = channel_def['name']
        url_path = channel_def['url_path']
        service_name = channel_def['service']

        logger.info('Creating channel: name=%s url_path=%s service=%s', name, url_path, service_name)

        service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).first()
        if not service:
            msg = f'Service not found {service_name} -> REST channel {name}'
            raise Exception(msg)

        channel = HTTPSOAP()
        channel.name = name
        channel.connection = 'channel'
        channel.transport = 'plain_http'
        channel.url_path = url_path
        channel.service = service
        channel.cluster = self.importer.get_cluster(session)
        channel.is_active = True
        channel.is_internal = False
        channel.soap_action = 'not-used'

        for key, value in channel_def.items():
            if key not in ['service', 'security']:
                setattr(channel, key, value)

        if 'security' in channel_def:
            security_name = channel_def['security']
            if security_name not in self.importer.sec_defs:
                raise Exception(f'Security definition "{security_name}" not found for REST channel "{name}"')

            sec_def = self.importer.sec_defs[security_name]
            channel.security_id = sec_def['id']

        session.add(channel)
        return channel

# ################################################################################################################################

    def update_channel_rest(self, channel_def:'anydict', session:'SASession') -> 'any_':
        channel_id = channel_def['id']

        channel = session.query(HTTPSOAP).filter_by(id=channel_id).one()

        channel.url_path = channel_def['url_path']

        service_name = channel_def['service']
        service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).first()
        if not service:
            raise Exception(f'Service not found: {service_name}')
        channel.service = service

        for key, value in channel_def.items():
            if key not in ['id', 'service', 'security']:
                setattr(channel, key, value)

        if 'security' in channel_def:
            security_name = channel_def['security']
            if security_name not in self.importer.sec_defs:
                raise Exception(f'Security definition "{security_name}" not found for REST channel "{channel_def["name"]}"')

            sec_def = self.importer.sec_defs[security_name]
            channel.security_id = sec_def['id']

        session.add(channel)
        return channel

# ################################################################################################################################

    def sync_channel_rest(self, channel_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d REST channels from YAML', len(channel_list))

        db_channels = self.get_rest_channels_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_channel_rest(channel_list, db_channels)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new REST channels', len(to_create))
            for item in to_create:
                logger.info('Creating channel: name=%s', item['name'])
                instance = self.create_channel_rest(item, session)
                logger.info('Created channel: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

            logger.info('Updating %d existing REST channels', len(to_update))
            for item in to_update:
                logger.info('Updating channel: name=%s id=%s', item['name'], item['id'])
                instance = self.update_channel_rest(item, session)
                logger.info('Updated channel: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing REST channels: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
