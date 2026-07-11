# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from json import loads

# Zato
from zato.cli.enmasse.util import preprocess_item, security_needs_update
from zato.common.api import CONNECTION, URL_TYPE
from zato.common.odb.model import HTTPSOAP, Service, to_json
from zato.common.util.sql import get_security_by_id, set_instance_opaque_attrs

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.orm.session import Session as SASession
    from zato.cli.enmasse.importer import EnmasseYAMLImporter
    from zato.common.typing_ import any_, anydict, anylist, listtuple

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# Keys that never map to database columns directly - they are handled separately.
_non_column_keys = ('id', 'service', 'security', 'security_name')

# What a YAML definition means when it does not say otherwise.
_default_is_active = True

# ################################################################################################################################
# ################################################################################################################################

class ChannelAS4Importer:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer

# ################################################################################################################################

    def get_as4_channels_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':

        # Our response to produce
        out:'anydict' = {}

        logger.info('Retrieving AS4 channels from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP)
        query = query.filter(HTTPSOAP.cluster_id==cluster_id)
        query = query.filter(HTTPSOAP.connection==CONNECTION.CHANNEL)
        query = query.filter(HTTPSOAP.transport==URL_TYPE.AS4)

        channels = to_json(query, return_as_dict=True)
        logger.info('Processing %d AS4 channels', len(channels))

        for item in channels:
            item = item['fields']
            name = item['name']
            logger.info('Processing AS4 channel: %s (id=%s)', name, item['id'])

            # Unpack opaque attributes into top-level keys so comparisons see the AS4 fields
            # like the profile, serviced participants or the pasted PEM keystore material.
            if opaque1 := item.get('opaque1'):
                opaque = loads(opaque1)
                if opaque:
                    item.update(opaque)

            out[name] = item

        return out

# ################################################################################################################################

    def _service_needs_update(self, item:'anydict', db_def:'anydict', session:'SASession') -> 'bool':
        """ Returns True if the YAML routing service differs from the one the row points to.
        """
        yaml_service = item.get('service')

        db_service_name = None
        if db_service_id := db_def.get('service_id'):
            db_service = session.query(Service).filter_by(id=db_service_id).first()
            if db_service:
                db_service_name = db_service.name

        if yaml_service != db_service_name:
            logger.info('Service changed for AS4 channel %s: yaml=%s db=%s', item['name'], yaml_service, db_service_name)
            return True

        return False

# ################################################################################################################################

    def compare_channel_as4(self, yaml_defs:'anylist', db_defs:'anydict', session:'SASession') -> 'listtuple':
        to_create:'anylist' = []
        to_update:'anylist' = []

        logger.info('Comparing %d YAML AS4 channels with %d DB AS4 channels', len(yaml_defs), len(db_defs))

        for item in yaml_defs:

            item = preprocess_item(item)
            name = item['name']

            logger.info('Checking YAML AS4 channel: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('AS4 channel %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('AS4 channel %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                # Compare standard attributes - security and the routing service are checked separately.
                for key, value in item.items():

                    if key in _non_column_keys:
                        continue

                    # A field the database row does not have yet means an update too.
                    if key not in db_def:
                        logger.info('Field %s.%s not in DB yet, will update', name, key)
                        needs_update = True
                        break

                    if db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                # Check security definition
                if security_needs_update(item, db_def, self.importer):
                    needs_update = True

                # Check the routing service
                if self._service_needs_update(item, db_def, session):
                    needs_update = True

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

    def _assign_security(self, channel:'any_', channel_def:'anydict', session:'SASession') -> 'None':
        """ Assigns a security definition to the channel if the YAML definition names one.
        """
        if (security_name := channel_def.get('security')) is not None:
            logger.info('Security name found: %s', security_name)
            if security_name not in self.importer.sec_defs:
                logger.error('Security definition "%s" not found in sec_defs', security_name)
                raise Exception(f'Security definition "{security_name}" not found for AS4 channel "{channel_def["name"]}"')

            sec_def = self.importer.sec_defs[security_name]
            security_item = get_security_by_id(session, sec_def['id'])
            channel.security = security_item
            logger.info('Assigned security object with id %s to AS4 channel %s', sec_def['id'], channel_def['name'])
        else:
            logger.info('No security definition specified for AS4 channel %s', channel_def['name'])

# ################################################################################################################################

    def _get_service(self, channel_def:'anydict', session:'SASession') -> 'any_':
        """ Returns the routing service named in the YAML definition - AS4 channels
        may have none because their messages can go to a pub/sub topic instead.
        """
        service_name = channel_def.get('service')

        if not service_name:
            return None

        service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).first()
        if not service:
            raise Exception(f'Service not found: {service_name}')

        return service

# ################################################################################################################################

    def create_channel_as4(self, channel_def:'anydict', session:'SASession') -> 'any_':
        name = channel_def['name']
        logger.info('Creating AS4 channel: %s', name)
        logger.info('Channel definition: %s', channel_def)

        service = self._get_service(channel_def, session)
        cluster = self.importer.get_cluster(session)

        channel = HTTPSOAP(cluster=cluster, service=service)
        channel.name = name
        channel.connection = CONNECTION.CHANNEL
        channel.transport = URL_TYPE.AS4
        channel.url_path = channel_def['url_path']
        channel.soap_action = ''
        channel.is_active = channel_def.get('is_active', _default_is_active)
        channel.is_internal = False

        # Process standard attributes - the AS4 fields are not columns,
        # they travel to the opaque attributes below.
        for key, value in channel_def.items():
            if key not in _non_column_keys:
                setattr(channel, key, value)

        # Handle security definition
        self._assign_security(channel, channel_def, session)

        # Fields that are not columns go into the opaque attributes.
        set_instance_opaque_attrs(channel, channel_def)

        session.add(channel)

        return channel

# ################################################################################################################################

    def update_channel_as4(self, channel_def:'anydict', session:'SASession') -> 'any_':

        channel_id = channel_def['id']
        logger.info('Updating AS4 channel with id=%s', channel_id)
        logger.info('Channel definition: %s', channel_def)

        channel = session.query(HTTPSOAP).filter_by(id=channel_id).one()

        if url_path := channel_def.get('url_path'):
            channel.url_path = url_path

        # The routing service may be removed altogether, which routes to a topic instead.
        channel.service = self._get_service(channel_def, session)

        # Process standard attributes
        for key, value in channel_def.items():
            if key not in _non_column_keys:
                setattr(channel, key, value)

        # Handle security definition
        self._assign_security(channel, channel_def, session)

        # Fields that are not columns go into the opaque attributes,
        # merged with whatever the row already keeps there.
        set_instance_opaque_attrs(channel, channel_def)

        session.add(channel)

        return channel

# ################################################################################################################################

    def sync_channel_as4(self, channel_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d AS4 channels from YAML', len(channel_list))

        db_channels = self.get_as4_channels_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_channel_as4(channel_list, db_channels, session)

        out_created:'anylist' = []
        out_updated:'anylist' = []

        try:
            logger.info('Creating %d new AS4 channels', len(to_create))
            for item in to_create:
                logger.info('Creating AS4 channel: name=%s', item['name'])
                instance = self.create_channel_as4(item, session)
                logger.info('Created AS4 channel: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

            logger.info('Updating %d existing AS4 channels', len(to_update))
            for item in to_update:
                logger.info('Updating AS4 channel: name=%s id=%s', item['name'], item['id'])
                instance = self.update_channel_as4(item, session)
                logger.info('Updated AS4 channel: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        # A genuinely broad boundary - whatever failed while syncing,
        # the session must be rolled back before the error propagates.
        except Exception as e:
            logger.error('Error syncing AS4 channels: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        out = out_created, out_updated
        return out

# ################################################################################################################################
# ################################################################################################################################
