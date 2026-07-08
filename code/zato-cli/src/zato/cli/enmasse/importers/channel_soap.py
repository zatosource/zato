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
_non_column_keys = ('id', 'service', 'security', 'groups', 'rate_limiting', 'use_mtom')

# ################################################################################################################################
# ################################################################################################################################

class ChannelSOAPImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer

# ################################################################################################################################

    def get_soap_channels_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}
        logger.info('Retrieving SOAP channels from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP).\
            filter(HTTPSOAP.cluster_id==cluster_id).\
            filter(HTTPSOAP.connection==CONNECTION.CHANNEL).\
            filter(HTTPSOAP.transport==URL_TYPE.SOAP) # type: ignore
        channels = to_json(query, return_as_dict=True)
        logger.info('Processing %d SOAP channels', len(channels))

        for item in channels:
            item = item['fields']
            name = item['name']
            logger.info('Processing SOAP channel: %s (id=%s)', name, item['id'])

            # Unpack opaque attributes into top-level keys so comparisons see fields
            # like use_mtom, security groups or rate limiting definitions.
            if opaque1 := item.get('opaque1'):
                opaque = loads(opaque1)
                if opaque:
                    item.update(opaque)

            out[name] = item

        return out

# ################################################################################################################################

    def compare_channel_soap(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML SOAP channels with %d DB SOAP channels', len(yaml_defs), len(db_defs))

        for item in yaml_defs:

            item = preprocess_item(item)
            name = item['name']

            logger.info('Checking YAML SOAP channel: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('SOAP channel %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('SOAP channel %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                # Compare standard attributes - security, groups and rate limiting are checked separately
                # and the service name is not a column in the database row (only service_id is).
                for key, value in item.items():

                    if key in ('security', 'security_name', 'groups', 'rate_limiting', 'service'):
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

                # Check security groups
                if self._groups_need_update(item, db_def):
                    needs_update = True

                # Check rate_limiting
                if self._rate_limiting_needs_update(item, db_def):
                    needs_update = True

                if needs_update:
                    item['id'] = db_def['id']
                    logger.info('Will update %s with id=%s', name, db_def['id'])
                    to_update.append(item)
                else:
                    logger.info('No update needed for %s', name)

        logger.info('Comparison result: to_create=%d to_update=%d', len(to_create), len(to_update))
        return to_create, to_update

# ################################################################################################################################

    def _groups_need_update(self, item:'anydict', db_def:'anydict') -> 'bool':
        """ Check if security groups need update.
        """

        # Get groups from YAML
        yaml_groups = set(item.get('groups', []))

        # Get groups from DB - the DB definition already has its opaque attributes unpacked.
        db_groups = set()
        group_ids = db_def.get('security_groups', [])

        # Convert IDs to names
        for group_id in group_ids:
            for group_name, group_def in self.importer.group_defs.items():
                group_def_id = int(group_def['id'])
                group_id_int = int(group_id)
                if group_def_id == group_id_int:
                    db_groups.add(group_name)
                    break

        # Return True if groups differ
        if yaml_groups != db_groups:
            logger.info('Groups changed for SOAP channel %s: yaml=%s db=%s', item['name'], sorted(yaml_groups), sorted(db_groups))
            return True

        return False

# ################################################################################################################################

    def _rate_limiting_needs_update(self, item:'anydict', db_def:'anydict') -> 'bool':
        """ Check if rate_limiting needs update.
        """
        yaml_rate_limiting = item.get('rate_limiting', [])
        db_rate_limiting = db_def.get('rate_limiting', [])

        if yaml_rate_limiting != db_rate_limiting:
            logger.info('rate_limiting changed for SOAP channel %s', item['name'])
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
                    raise Exception(f'Security group "{group_name}" not found for SOAP channel "{channel_def["name"]}"')

                # Get the group ID
                group_id = self.importer.group_defs[group_name]['id']
                processed_security_groups.append(group_id)

        # Return what we have to our caller
        return processed_security_groups

# ################################################################################################################################

    def _build_opaque_attrs(self, channel_def:'anydict') -> 'anydict':
        """ Builds the dictionary of attributes stored in the channel's opaque field.
        """
        opaque_attrs = {}

        # The MTOM toggle for responses
        if 'use_mtom' in channel_def:
            opaque_attrs['use_mtom'] = channel_def['use_mtom']

        # Security groups
        if channel_def.get('groups'):
            security_groups = self._preprocess_security_groups(channel_def)
            opaque_attrs['security_groups'] = security_groups

        # Rate limiting
        if rate_limiting := channel_def.get('rate_limiting'):
            opaque_attrs['rate_limiting'] = rate_limiting

        return opaque_attrs

# ################################################################################################################################

    def _assign_security(self, channel:'any_', channel_def:'anydict', session:'SASession') -> 'None':
        """ Assigns a security definition to the channel if the YAML definition names one.
        """
        if (security_name := channel_def.get('security')) is not None:
            logger.info('Security name found: %s', security_name)
            if security_name not in self.importer.sec_defs:
                logger.error('Security definition "%s" not found in sec_defs', security_name)
                raise Exception(f'Security definition "{security_name}" not found for SOAP channel "{channel_def["name"]}"')

            sec_def = self.importer.sec_defs[security_name]
            security_item = get_security_by_id(session, sec_def['id'])
            channel.security = security_item
            logger.info('Assigned security object with id %s to SOAP channel %s', sec_def['id'], channel_def['name'])
        else:
            logger.info('No security definition specified for SOAP channel %s', channel_def['name'])

# ################################################################################################################################

    def create_channel_soap(self, channel_def:'anydict', session:'SASession') -> 'any_':
        name = channel_def['name']
        logger.info('Creating SOAP channel: %s', name)
        logger.info('Channel definition: %s', channel_def)

        service_name = channel_def['service']
        service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).one()
        cluster = self.importer.get_cluster(session)

        channel = HTTPSOAP(cluster=cluster, service=service)
        channel.name = name
        channel.connection = CONNECTION.CHANNEL
        channel.transport = URL_TYPE.SOAP
        channel.url_path = channel_def['url_path']
        channel.method = channel_def.get('method', '') or ''
        channel.is_active = True
        channel.is_internal = False

        # Required SOAP-specific fields
        channel.soap_action = channel_def.get('soap_action', '')
        channel.soap_version = channel_def.get('soap_version', '1.1')

        # Process standard attributes
        for key, value in channel_def.items():
            if key not in _non_column_keys:
                setattr(channel, key, value)

        # Handle security definition
        self._assign_security(channel, channel_def, session)

        # Fields that are not columns go into the opaque attributes.
        opaque_attrs = self._build_opaque_attrs(channel_def)
        if opaque_attrs:
            set_instance_opaque_attrs(channel, opaque_attrs)

        session.add(channel)
        return channel

# ################################################################################################################################

    def update_channel_soap(self, channel_def:'anydict', session:'SASession') -> 'any_':

        channel_id = channel_def['id']
        logger.info('Updating SOAP channel with id=%s', channel_id)
        logger.info('Channel definition: %s', channel_def)

        channel = session.query(HTTPSOAP).filter_by(id=channel_id).one()

        if url_path := channel_def.get('url_path'):
            channel.url_path = url_path

        if service_name := channel_def.get('service'):
            service = session.query(Service).filter_by(name=service_name, cluster_id=self.importer.cluster_id).first()
            if not service:
                raise Exception(f'Service not found: {service_name}')
            channel.service = service

        # Process standard attributes
        for key, value in channel_def.items():
            if key not in _non_column_keys:
                setattr(channel, key, value)

        # Handle security definition
        self._assign_security(channel, channel_def, session)

        # Fields that are not columns go into the opaque attributes,
        # merged with whatever the row already keeps there.
        opaque_attrs = self._build_opaque_attrs(channel_def)
        if opaque_attrs:
            set_instance_opaque_attrs(channel, opaque_attrs)

        session.add(channel)
        return channel

# ################################################################################################################################

    def sync_channel_soap(self, channel_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d SOAP channels from YAML', len(channel_list))

        db_channels = self.get_soap_channels_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_channel_soap(channel_list, db_channels)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new SOAP channels', len(to_create))
            for item in to_create:
                logger.info('Creating SOAP channel: name=%s', item['name'])
                instance = self.create_channel_soap(item, session)
                logger.info('Created SOAP channel: name=%s id=%s security_id=%s', instance.name, instance.id, instance.security_id)
                out_created.append(instance)

            logger.info('Updating %d existing SOAP channels', len(to_update))
            for item in to_update:
                logger.info('Updating SOAP channel: name=%s id=%s', item['name'], item['id'])
                instance = self.update_channel_soap(item, session)
                logger.info('Updated SOAP channel: name=%s id=%s security_id=%s', instance.name, instance.id, instance.security_id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing SOAP channels: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
