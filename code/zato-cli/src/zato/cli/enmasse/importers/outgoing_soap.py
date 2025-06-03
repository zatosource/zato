# -*- coding: utf-8 -*-

"""
Copyright (C) 2025, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from copy import deepcopy

# Zato
from zato.common.api import CONNECTION, HTTP_SOAP_SERIALIZATION_TYPE, URL_TYPE
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

class OutgoingSOAPImporter:

    def __init__(self, importer:'EnmasseYAMLImporter') -> 'None':
        self.importer = importer
        self.connection_defs = {}

# ################################################################################################################################

    def get_outgoing_soap_from_db(self, session:'SASession', cluster_id:'int') -> 'anydict':
        out = {}
        logger.info('Retrieving outgoing SOAP connections from database for cluster_id=%s', cluster_id)

        query = session.query(HTTPSOAP).filter(HTTPSOAP.cluster_id==cluster_id).filter(HTTPSOAP.connection==CONNECTION.OUTGOING).filter(HTTPSOAP.transport==URL_TYPE.SOAP) # type: ignore
        connections = to_json(query, return_as_dict=True)
        logger.info('Processing %d outgoing SOAP connections', len(connections))

        for item in connections:
            item = item['fields']
            name = item['name']
            logger.info('Processing outgoing SOAP connection: %s (id=%s)', name, item['id'])
            out[name] = item
            self.connection_defs[name] = item

        return out

# ################################################################################################################################

    def _security_needs_update(self, item:'anydict', db_def:'anydict') -> 'bool':
        # Check if security definition needs update.
        yaml_security = item.get('security')
        db_security_id = db_def.get('security_id')

        # If security is not defined in YAML but exists in DB - update needed
        if yaml_security is None and db_security_id is not None:
            logger.info('Security removed in YAML but exists in DB')
            return True

        # If security is defined in YAML but not in DB - update needed
        elif yaml_security is not None and db_security_id is None:
            logger.info('Security defined in YAML but missing in DB')
            return True

        # If security is defined in both, check if they match
        elif yaml_security is not None and db_security_id is not None:
            if yaml_security not in self.importer.sec_defs:
                logger.warning('Security definition %s not found, skipping comparison', yaml_security)
                return False

            sec_def = self.importer.sec_defs[yaml_security]
            if sec_def['id'] != db_security_id:
                logger.info('Security mismatch: YAML=%s DB_ID=%s', yaml_security, db_security_id)
                return True

        return False

    def compare_outgoing_soap(self, yaml_defs:'anylist', db_defs:'anydict') -> 'listtuple':
        to_create = []
        to_update = []

        logger.info('Comparing %d YAML outgoing SOAP connections with %d DB outgoing SOAP connections', len(yaml_defs), len(db_defs))

        for item in yaml_defs:
            name = item['name']
            logger.info('Checking YAML outgoing SOAP connection: name=%s', name)

            db_def = db_defs.get(name)

            if not db_def:
                logger.info('Outgoing SOAP connection %s not found in DB, will create new', name)
                to_create.append(item)
            else:
                logger.info('Outgoing SOAP connection %s exists in DB with id=%s', name, db_def['id'])

                needs_update = False

                # Compare standard attributes (excluding security)
                for key, value in item.items():
                    if key != 'security' and key in db_def and db_def[key] != value:
                        logger.info('Value mismatch for %s.%s: YAML=%s DB=%s', name, key, value, db_def[key])
                        needs_update = True
                        break

                # Check security definition
                if self._security_needs_update(item, db_def):
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

    def create_outgoing_soap(self, outgoing_def:'anydict', session:'SASession') -> 'any_':
        sss
        name = outgoing_def['name']
        logger.info('Creating outgoing SOAP connection: %s', name)

        # No extra fields yet
        connection_extra_field_defaults = {
        }

        outgoing = HTTPSOAP()
        outgoing.name = name
        outgoing.is_active = outgoing_def.get('is_active', True)
        outgoing.connection = CONNECTION.OUTGOING
        outgoing.transport = URL_TYPE.SOAP
        outgoing.cluster = self.importer.get_cluster(session)
        outgoing.merge_url_params_req = outgoing_def.get('merge_url_params_req', True)
        outgoing.has_rbac = outgoing_def.get('has_rbac', False)
        outgoing.tls_verify = outgoing_def.get('tls_verify', True)
        outgoing.serialization_type = outgoing_def.get('serialization_type', HTTP_SOAP_SERIALIZATION_TYPE.SUDS.id)
        outgoing.is_internal = outgoing_def.get('is_internal', False)

        # Required SOAP-specific fields
        outgoing.soap_action = outgoing_def.get('soap_action', '')
        outgoing.soap_version = outgoing_def.get('soap_version', '1.1')

        # Set default values that may not be provided
        outgoing.ping_method = outgoing_def.get('ping_method', 'GET')
        outgoing.pool_size = outgoing_def.get('pool_size', 20)
        outgoing.timeout = outgoing_def.get('timeout', 60)

        # Copy other defined attributes
        for key, value in outgoing_def.items():
            if key not in ['security', 'security_name']:
                setattr(outgoing, key, value)

        if 'security' in outgoing_def or 'security_name' in outgoing_def:
            print()
            zzz
            security_name = outgoing_def.get('security') or outgoing_def.get('security_name')
            if security_name not in self.importer.sec_defs:
                error_msg = f'Security definition "{security_name}" not found for outgoing SOAP connection "{name}"'
                logger.error(error_msg)
                raise Exception(error_msg)
            sec_def = self.importer.sec_defs[security_name]
            outgoing.security_id = sec_def['id']

        outgoing_def = deepcopy(outgoing_def)
        outgoing_def.update(connection_extra_field_defaults)

        set_instance_opaque_attrs(outgoing, outgoing_def)

        session.add(outgoing)
        self.connection_defs[name] = outgoing
        return outgoing

# ################################################################################################################################

    def update_outgoing_soap(self, outgoing_def:'anydict', session:'SASession') -> 'any_':
        outgoing_id = outgoing_def['id']
        name = outgoing_def['name']
        logger.info('Updating outgoing SOAP connection: %s (id=%s)', name, outgoing_id)

        outgoing = session.query(HTTPSOAP).filter_by(id=outgoing_id).one()

        for key, value in outgoing_def.items():
            if key not in ['security', 'security_name']:
                setattr(outgoing, key, value)

        if 'security' in outgoing_def or 'security_name' in outgoing_def:
            security_name = outgoing_def.get('security') or outgoing_def.get('security_name')
            if security_name not in self.importer.sec_defs:
                error_msg = f'Security definition "{security_name}" not found for outgoing SOAP connection "{name}"'
                logger.error(error_msg)
                raise Exception(error_msg)
            sec_def = self.importer.sec_defs[security_name]
            outgoing.security_id = sec_def['id']

        session.add(outgoing)
        self.connection_defs[name] = outgoing
        return outgoing

# ################################################################################################################################

    def sync_outgoing_soap(self, outgoing_list:'anylist', session:'SASession') -> 'listtuple':
        logger.info('Processing %d outgoing SOAP connections from YAML', len(outgoing_list))

        db_outgoing = self.get_outgoing_soap_from_db(session, self.importer.cluster_id)
        to_create, to_update = self.compare_outgoing_soap(outgoing_list, db_outgoing)

        out_created = []
        out_updated = []

        try:
            logger.info('Creating %d new outgoing SOAP connections', len(to_create))
            for item in to_create:
                logger.info('Creating outgoing SOAP connection: name=%s', item['name'])
                instance = self.create_outgoing_soap(item, session)
                logger.info('Created outgoing SOAP connection: name=%s id=%s', instance.name, instance.id)
                out_created.append(instance)

            logger.info('Updating %d existing outgoing SOAP connections', len(to_update))
            for item in to_update:
                logger.info('Updating outgoing SOAP connection: name=%s id=%s', item['name'], item['id'])
                instance = self.update_outgoing_soap(item, session)
                logger.info('Updated outgoing SOAP connection: name=%s id=%s', instance.name, instance.id)
                out_updated.append(instance)

            logger.info('Committing changes: created=%d updated=%d', len(out_created), len(out_updated))
            session.commit()
            logger.info('Successfully committed all changes')

        except Exception as e:
            logger.error('Error syncing outgoing SOAP connections: %s', e)
            logger.exception('Full exception details:')
            session.rollback()
            raise

        return out_created, out_updated

# ################################################################################################################################
# ################################################################################################################################
