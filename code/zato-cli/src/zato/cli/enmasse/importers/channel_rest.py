# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from json import loads
import logging

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

# ################################################################################################################################
# ################################################################################################################################

class ChannelImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer

# ################################################################################################################################

    def get_rest_channels_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}
        logger.info('Retrieving REST channels from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP).filter(HTTPSOAP.cluster_id==cluster_id).filter(HTTPSOAP.connection==CONNECTION.CHANNEL).filter(HTTPSOAP.transport==URL_TYPE.PLAIN_HTTP) # type: ignore
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

            item = preprocess_item(item)
            name = item['name']

            logger.info('Checking YAML channel: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Channel %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Channel %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                # Compare standard attributes (excluding security and groups)
                for key, value in item.items():
                    if key not in ['security', 'groups'] and key in db_def and db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                # Check security definition
                if security_needs_update(item, db_def, self.importer):
                    needs_update = True

                # Check security groups
                if self._groups_need_update(item, db_def):
                    needs_update = True

                if needs_update:
                    item['id'] = db_def['id']  # Add ID to original item
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)  # Keep original item with env vars for update
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))
        return to_create, to_update

    def _groups_need_update(self, item, db_def):
        """ Check if security groups need update.
        """

        # Get groups from YAML
        yaml_groups = set(item.get('groups', []))

        # Get groups from DB
        db_groups = set()
        try:
            opaque1 = db_def.get('opaque1')
            if opaque1:
                opaque = loads(opaque1)
                group_ids = opaque.get('security_groups', [])

                # Convert IDs to names
                for group_id in group_ids:
                    for group_name, group_def in self.importer.group_defs.items():
                        group_def_id = int(group_def['id'])
                        group_id_int = int(group_id)
                        if group_def_id == group_id_int:
                            db_groups.add(group_name)
                            break
        except Exception as e:
            logger.warning('Error parsing opaque for channel %s: %s', item['name'], e)

        # Return True if groups differ
        if yaml_groups != db_groups:
            logger.info('Groups changed for channel %s: yaml=%s db=%s', item['name'], sorted(yaml_groups), sorted(db_groups))
            return True

        return False

# ################################################################################################################################

    def _preprocess_security_groups(self, channel_def:'anydict') -> 'list':
        """ Convert security group names to IDs.
        """
        # This will contain only IDs
        processed_security_groups = []

        # Security groups are optional
        if 'groups' in channel_def and channel_def['groups']:

            # Get information about existing security groups
            for group_name in channel_def['groups']:

                # Check if group exists in importer's groups
                if group_name not in self.importer.group_defs:
                    raise Exception(f'Security group "{group_name}" not found for REST channel "{channel_def["name"]}"')

                # Get the group ID
                group_id = self.importer.group_defs[group_name]['id']
                processed_security_groups.append(group_id)

        # Return what we have to our caller
        return processed_security_groups

    def create_channel_rest(self, channel_def:'anydict', session:'SASession') -> 'any_':
        name = channel_def['name']
        logger.info('Creating REST channel: %s', name)
        logger.info('Channel definition: %s', channel_def)

        service_name = channel_def['service']
        service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).one()
        cluster = self.importer.get_cluster(session)

        security_item = None
        if security_name := channel_def.get('security'):
            logger.info('Security name found: %s', security_name)
            if security_name not in self.importer.sec_defs:
                logger.error('Security definition "%s" not found in sec_defs', security_name)
                raise Exception(f'Security definition "{security_name}" not found for REST channel "{name}"')
            sec_def = self.importer.sec_defs[security_name]
            logger.info('Found security definition: %s', sec_def)
            security_item = get_security_by_id(session, sec_def['id'])
            logger.info('Retrieved security object with id %s for channel %s', sec_def['id'], name)
        else:
            logger.info('No security definition specified for channel %s', name)

        channel = HTTPSOAP(cluster=cluster, service=service)
        channel.name = name
        channel.connection = CONNECTION.CHANNEL
        channel.transport = URL_TYPE.PLAIN_HTTP
        channel.url_path = channel_def['url_path']
        channel.method = channel_def.get('method', '') or ''
        channel.is_active = True
        channel.is_internal = False
        channel.soap_action = '' # Must be an empty string

        # Process standard attributes
        for key, value in channel_def.items():
            if key not in ['service', 'security', 'groups']:
                setattr(channel, key, value)

        if security_item:
            channel.security = security_item
            logger.info('Assigned security object to channel %s', name)

        logger.info('Channel created with security_id=%s', channel.security_id)

        # Handle security groups
        if channel_def.get('groups'):
            security_groups = self._preprocess_security_groups(channel_def)

            # Create an object to store in opaque1
            opaque_attrs = {'security_groups': security_groups}
            set_instance_opaque_attrs(channel, opaque_attrs)

        session.add(channel)
        return channel

# ################################################################################################################################

    def update_channel_rest(self, channel_def:'anydict', session:'SASession') -> 'any_':

        channel_id = channel_def['id']
        logger.info('Updating REST channel with id=%s', channel_id)
        logger.info('Channel definition: %s', channel_def)

        channel = session.query(HTTPSOAP).filter_by(id=channel_id).one()
        logger.info('Current channel security_id before update: %s', channel.security_id)

        channel.url_path = channel_def['url_path']

        service_name = channel_def['service']
        service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).first()
        if not service:
            raise Exception(f'Service not found: {service_name}')
        channel.service = service

        # Process standard attributes
        for key, value in channel_def.items():
            if key not in ['id', 'service', 'security', 'groups']:
                setattr(channel, key, value)

        # Handle security definition
        logger.info('Checking for security in channel_def: %s', channel_def.get('security'))
        logger.info('Available security definitions: %s', list(self.importer.sec_defs.keys()))
        if (security_name := channel_def.get('security')) is not None:
            logger.info('Security name found: %s', security_name)
            if security_name not in self.importer.sec_defs:
                logger.error('Security definition "%s" not found in sec_defs', security_name)
                raise Exception(f'Security definition "{security_name}" not found for REST channel "{channel_def["name"]}"')

            sec_def = self.importer.sec_defs[security_name]
            logger.info('Found security definition: %s', sec_def)
            security_item = get_security_by_id(session, sec_def['id'])
            channel.security = security_item
            logger.info('Set security object for channel %s with id %s', channel_def['name'], sec_def['id'])
            logger.info('Channel security_id after assignment: %s', channel.security_id)
        else:
            logger.info('No security definition specified for channel %s', channel_def['name'])

        # Handle security groups
        if (groups := channel_def.get('groups')) is not None and groups:
            security_groups = self._preprocess_security_groups(channel_def)
            # Create an object to store in opaque1
            opaque_attrs = {'security_groups': security_groups}
            set_instance_opaque_attrs(channel, opaque_attrs)

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
                logger.info('Created channel: name=%s id=%s security_id=%s', instance.name, instance.id, instance.security_id)
                out_created.append(instance)

            logger.info('Updating %d existing REST channels', len(to_update))
            for item in to_update:
                logger.info('Updating channel: name=%s id=%s', item['name'], item['id'])
                instance = self.update_channel_rest(item, session)
                logger.info('Updated channel: name=%s id=%s security_id=%s', instance.name, instance.id, instance.security_id)
                out_updated.append(instance)

            logger.info('Flushing session before commit')
            session.flush()
            logger.info('After flush, checking instances')
            for instance in out_created + out_updated:
                logger.info('After flush - channel: name=%s id=%s security_id=%s', instance.name, instance.id, instance.security_id)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

            logger.info('Verifying channels in database after commit')
            for instance in out_created + out_updated:
                session.refresh(instance)
                logger.info('Verified channel: name=%s id=%s security_id=%s', instance.name, instance.id, instance.security_id)

        except Exception as e:
            logger.error('Error syncing REST channels: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
